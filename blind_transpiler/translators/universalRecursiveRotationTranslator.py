from math import pi
from ..essentials.bop import BOP
from .base import BaseTranslator
from .homomorphicTranslator import HomomorphicTranslation
from ..global_value_store import GlobalVariablesAndFunctions

# class UBQC_AR(BaseTranslator):
class UniversalRecursiveRotationTranslator(BaseTranslator):
    '''
    Library class for full-blind quantum computation.
    Build on top of HomomorphicTranslation class.
    Inheritance of above class can be taken, but might be a bad idea.
    Logic is based on paper:
        
        Joshi, Mohit, Manoj Kumar Mishra, and S. Karthikeyan. "Universal Blind Quantum Computation with Recursive Rotation Gates." arXiv preprint arXiv:2512.15101 (2025).

    Assumes constant compute space of 11 ancilla qubits. Note, s,t can be removed as rz can implement them also:
        added 'rz' gate in resource set which was not present in the literature, 
        this will help practical universal computation
        the fdqc compute space is 11, now,
        if any update is done here also change the 'constant_compute_space' in BQC.fdqc()

    This uses an optimized version of algorithm given in paper 'universal blind quantum computation using recursive rotation gates' that uses omly M gate instead of M^2
        
    '''
    def __init__(self):
        GVF = GlobalVariablesAndFunctions()

        self.constant_compute_space = GVF.ubqc_compute_space   # Note: This space can be reduce to 9 as rz can perform s,t gate also.
        self.ri = {'h':(0,), 'cz':(1,2), 'rz':(3,)}  # resource_index: index of resource in server.
        self.M = GVF.M


    def h(self, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 'h' gate for ubqc.
        Needed size of encryption key = 2

        Args:
            key: list[int] - contains randomly generated binary keys, each element can be 0 or 1.
            qargs: list[int] - contains the argument on which the key has to be applied.
            gate_seq: int - used to store the information of which gate from original circuit, this translation is coming from.

        Return:
            Tuple[BOP] - tuple of BOP class object sequence needed for encryption, compute and decryption of the 'h' gate.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library - SwapGate

        '''
        from qiskit.circuit.library import  SwapGate, XGate, ZGate

        ri = self.ri

        x_key = [key[i] for i in range(len(key)) if i % 2 == 0]
        z_key = [key[i] for i in range(len(key)) if i % 2 != 0]

        s = [0 for s in range(self.M)]
        q = [0 for s in range(self.M)]

        full_variable_unroll = []

        full_variable_unroll.append(BOP('enc', (qargs[0],), [],  XGate(), x_key[0], gate_seq=gate_seq))
        full_variable_unroll.append(BOP('enc', (qargs[0],), [],  ZGate(), z_key[0], gate_seq=gate_seq))
        full_variable_unroll.append(BOP('swap', (qargs[0],ri['h'][0]), [], SwapGate(), 1,gate_seq=gate_seq ))
        full_variable_unroll.append(self._server_constant_resource_set(gate_seq=gate_seq))
        full_variable_unroll.append(BOP('swap', (qargs[0],ri['h'][0]), [], SwapGate(), 1,gate_seq=gate_seq ))
        full_variable_unroll.append(BOP('dec', (qargs[0],), [],  XGate(), z_key[0], gate_seq=gate_seq))
        full_variable_unroll.append(BOP('dec', (qargs[0],), [],  ZGate(), x_key[0], gate_seq=gate_seq))

        for m in range(self.M, 0,-1):
            full_variable_unroll.append(BOP('enc', (qargs[0],), [],  XGate(), x_key[m], gate_seq=gate_seq))
            full_variable_unroll.append(BOP('enc', (qargs[0],), [],  ZGate(), z_key[m], gate_seq=gate_seq))
            full_variable_unroll.append(self._server_recursive_resource_set(gate_seq=gate_seq,k_for_theta=m))
            full_variable_unroll.append(BOP('enc', (qargs[0],), [],  ZGate(), z_key[m], gate_seq=gate_seq))
            full_variable_unroll.append(BOP('enc', (qargs[0],), [],  XGate(), x_key[m], gate_seq=gate_seq))

        full_variable_unroll = tuple(full_variable_unroll)
        return full_variable_unroll
        


    def rz(self, theta, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 'rz' gate for ubqc.
        Needed size of encryption key = need variable length.


        Args:
            theta: float - contain the theta parameter (in radian) to apply theta rotation on the circuit.
            key: list[int] - contains randomly generated binary keys, each element can be 0 or 1. Size should be 2M
            qargs: list[int] - contains the argument on which the key has to be applied.
            gate_seq: int - used to store the information of which gate from original circuit, this translation is coming from.

        Return:
            Tuple[BOP] - tuple of BOP class object sequence needed for encryption, compute and decryption of the 'rz' gate.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library - SwapGate

        '''
        from qiskit.circuit.library import SwapGate, XGate, ZGate
        from math import ceil, pi,log # remove this line after testing

        ri = self.ri

        # convert the angle to binary representation 
        binary, int_part =self._decompose_theta(theta)  # precision can also be asked from user

        s = [1 if (x==1 or x==-1) else 0 for x in binary]
        q = [1 if x == -1 else 0 for x in binary]

        # pad s and q, to allow easy algo writing as R_z(pi/2^k)
        # padding at first place will have no physical meaning
        # just a trip to get by algorithm design easily
        s.insert(0,0)
        q.insert(0,0)

        x_key = [key[i] for i in range(len(key)) if i % 2 == 0]
        z_key = [key[i] for i in range(len(key)) if i % 2 != 0]

        full_variable_unroll = []

        # no work on client data is done here, enc and dec are used just for assurity that server sees diff inputs everytime.
        full_variable_unroll.append(BOP('enc', (qargs[0],), [],  XGate(), x_key[0], gate_seq=gate_seq))
        full_variable_unroll.append(BOP('enc', (qargs[0],), [],  ZGate(), z_key[0], gate_seq=gate_seq))
        full_variable_unroll.append(self._server_constant_resource_set(gate_seq=gate_seq))
        full_variable_unroll.append(BOP('dec', (qargs[0],), [],  ZGate(), z_key[0], gate_seq=gate_seq))
        full_variable_unroll.append(BOP('dec', (qargs[0],), [],  XGate(), x_key[0], gate_seq=gate_seq))


        M = len(binary)

        # handle integral part
        if int_part % 2 == 1:
            full_variable_unroll.append(BOP('client', (qargs[0],), [],  ZGate(), 1, gate_seq=gate_seq))



        for m in range(M, 0,-1):
            if s[m] == 0:
                pass # no need to do anything if angle is not present
                # this logic is written just for clarity
            if s[m] == 1:
                # gate before m will be implemented but not used:
                for k in range(M,m,-1):
                    full_variable_unroll.append(BOP('enc', (qargs[0],), [],  XGate(), x_key[k], gate_seq=gate_seq))
                    full_variable_unroll.append(BOP('enc', (qargs[0],), [],  ZGate(), z_key[k], gate_seq=gate_seq))
                    full_variable_unroll.append(self._server_recursive_resource_set(gate_seq=gate_seq,k_for_theta=k))
                    full_variable_unroll.append(BOP('dec', (qargs[0],), [],  ZGate(), z_key[k], gate_seq=gate_seq))
                    full_variable_unroll.append(BOP('dec', (qargs[0],), [],  XGate(), x_key[k], gate_seq=gate_seq))

                # gate after m will be implemented depending on run_of_one
                run_of_one = False
                full_variable_unroll.append(BOP('enc', (qargs[0],), [],  XGate(), x_key[m], gate_seq=gate_seq))
                full_variable_unroll.append(BOP('enc', (qargs[0],), [],  ZGate(), z_key[m], gate_seq=gate_seq))
                full_variable_unroll.append(BOP('swap', (qargs[0],ri['rz'][0]), [], SwapGate(), s[m],gate_seq=gate_seq ))
                full_variable_unroll.append(self._server_recursive_resource_set(gate_seq=gate_seq,k_for_theta=m))
                full_variable_unroll.append(BOP('swap', (qargs[0],ri['rz'][0]), [], SwapGate(), s[m],gate_seq=gate_seq ))
                full_variable_unroll.append(BOP('dec', (qargs[0],), [],  ZGate(), z_key[m], gate_seq=gate_seq))
                full_variable_unroll.append(BOP('dec', (qargs[0],), [],  XGate(), x_key[m], gate_seq=gate_seq))
                if (x_key[m]^q[m]) == 1:
                    run_of_one = True

                # for recursive correction of 2\theta  
                for k in range(m-1, 0, -1 ):
                    if run_of_one == True:
                        cond = s[m]&(x_key[k+1]^q[m])
                        full_variable_unroll.append(BOP('enc', (qargs[0],), [],  XGate(), x_key[k], gate_seq=gate_seq))
                        full_variable_unroll.append(BOP('enc', (qargs[0],), [],  ZGate(), z_key[k], gate_seq=gate_seq))
                        full_variable_unroll.append(BOP('swap', (qargs[0],ri['rz'][0]), [], SwapGate(), cond ,gate_seq=gate_seq ))
                        full_variable_unroll.append(self._server_recursive_resource_set(gate_seq=gate_seq,k_for_theta=k))
                        full_variable_unroll.append(BOP('swap', (qargs[0],ri['rz'][0]), [], SwapGate(), cond,gate_seq=gate_seq ))
                        full_variable_unroll.append(BOP('dec', (qargs[0],), [],  ZGate(), z_key[k], gate_seq=gate_seq))
                        full_variable_unroll.append(BOP('dec', (qargs[0],), [],  XGate(), x_key[k], gate_seq=gate_seq))
                        if s[m]&(x_key[k]^q[m]) == 0:
                            run_of_one = False 

                    if run_of_one == False:
                        full_variable_unroll.append(BOP('enc', (qargs[0],), [],  XGate(), x_key[k], gate_seq=gate_seq))
                        full_variable_unroll.append(BOP('enc', (qargs[0],), [],  ZGate(), z_key[k], gate_seq=gate_seq))
                        full_variable_unroll.append(self._server_recursive_resource_set(gate_seq=gate_seq,k_for_theta=k))
                        full_variable_unroll.append(BOP('dec', (qargs[0],), [],  ZGate(), z_key[k], gate_seq=gate_seq))
                        full_variable_unroll.append(BOP('dec', (qargs[0],), [],  XGate(), x_key[k], gate_seq=gate_seq))
                
                # last Z correction
                if run_of_one == True:
                    full_variable_unroll.append(BOP('client', (qargs[0],), [],  ZGate(), s[m], gate_seq=gate_seq))
   

        full_variable_unroll = tuple(full_variable_unroll)
        return full_variable_unroll



    def cz(self, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 'cz' gate for ubqc.
        Needed size of encryption key = 4

        Args:
            key: list[int] - contains randomly generated binary keys, each element can be 0 or 1.
            qargs: list[int] - contains the argument on which the key has to be applied.
            gate_seq: int - used to store the information of which gate from original circuit, this translation is coming from.

        Return:
            Tuple[BOP] - tuple of BOP class object sequence needed for encryption, compute and decryption of the 'cz' gate.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library - SwapGate

        '''
        from qiskit.circuit.library import SwapGate, XGate, ZGate
        ri = self.ri



        x_key = [key[i] for i in range(len(key)) if i % 2 == 0]
        z_key = [key[i] for i in range(len(key)) if i % 2 != 0]

        s = [0 for s in range(self.M)]
        q = [0 for s in range(self.M)]

        full_variable_unroll = []

        full_variable_unroll.append(BOP('enc', (qargs[0],), [],  XGate(), x_key[0], gate_seq=gate_seq))
        full_variable_unroll.append(BOP('enc', (qargs[0],), [],  ZGate(), z_key[0], gate_seq=gate_seq))
        full_variable_unroll.append(BOP('enc', (qargs[1],), [],  XGate(), x_key[1], gate_seq=gate_seq))
        full_variable_unroll.append(BOP('enc', (qargs[1],), [],  ZGate(), z_key[1], gate_seq=gate_seq))
        full_variable_unroll.append(BOP('swap', (qargs[0],ri['cz'][0]), [], SwapGate(),1 ,gate_seq=gate_seq ))
        full_variable_unroll.append(BOP('swap', (qargs[1],ri['cz'][1]), [], SwapGate(), 1,gate_seq=gate_seq ))
        full_variable_unroll.append(self._server_constant_resource_set(gate_seq=gate_seq))
        full_variable_unroll.append(BOP('swap', (qargs[0],ri['cz'][0]), [], SwapGate(), 1, gate_seq=gate_seq ))
        full_variable_unroll.append(BOP('swap', (qargs[1],ri['cz'][1]), [], SwapGate(), 1,gate_seq=gate_seq ))
        full_variable_unroll.append(BOP('dec', (qargs[0],), [],  ZGate(), z_key[0]^x_key[1], gate_seq=gate_seq))
        full_variable_unroll.append(BOP('dec', (qargs[0],), [],  XGate(), x_key[0], gate_seq=gate_seq))
        full_variable_unroll.append(BOP('dec', (qargs[1],), [],  ZGate(), z_key[1]^x_key[0], gate_seq=gate_seq))
        full_variable_unroll.append(BOP('dec', (qargs[1],), [],  XGate(), x_key[1], gate_seq=gate_seq))

        for m in range(self.M, 0,-1):
            full_variable_unroll.append(BOP('enc', (qargs[0],), [],  XGate(), x_key[m], gate_seq=gate_seq))
            full_variable_unroll.append(BOP('enc', (qargs[0],), [],  ZGate(), z_key[m], gate_seq=gate_seq))
            full_variable_unroll.append(self._server_recursive_resource_set(gate_seq=gate_seq,k_for_theta=m))
            full_variable_unroll.append(BOP('enc', (qargs[0],), [],  ZGate(), z_key[m], gate_seq=gate_seq))
            full_variable_unroll.append(BOP('enc', (qargs[0],), [],  XGate(), x_key[m], gate_seq=gate_seq))

        full_variable_unroll = tuple(full_variable_unroll)
        return full_variable_unroll


    # utility functions

    def _create_qubit_map(self, new_qargs):
        '''
        (Same as HomomorphicTranslation._create_qubit_map function)
        Creates a map between old and new qargs to be used for update the position of operation.
        This is used if place like cx(1,2) has to applies but library is made such that it implements cx(0,1), this function ensures hassle-free proper translation.
        Note: old qargs are assumed to be in sequencial order as 0,1,2,3...

        Args:
            new_qargs: List[int] - store new qubit position, according to above example store [1,2]

        Return:
            Dict[int->int] - dictionary map of old_qubit->new_qubit

        Raise: 
            None
            
        Library Dependency:
            None

        '''
        qarg_map = {}
        for i, qargs in enumerate(new_qargs):
            qarg_map[i] = qargs
        return qarg_map

    def _server_constant_resource_set(self, gate_seq):
        '''
        Creates server gate circuit.

        Args:
            gate_seq: int - used to store the information of which gate from original circuit, this translation is coming from.
            theta: float - contain the theta parameter (in radian) to apply theta rotation on the circuit. (Default = 2pi)

        Return:
            BOP - BOP class with modified conditional
            for better visualization Tuple[BOP] can also be used.

        Raise: 
            None
            
        Library Dependency:
            qiskit.circuit.library  - HGate, CXGate, CZGate, CCXGate, RZGate, TGate
            qiskit - QuantumCircuit
            math - pi
        '''
        from qiskit.circuit.library import HGate, CXGate, CZGate, CCXGate, RZGate, TGate
        from qiskit import QuantumCircuit
        from math import pi

        ri = self.ri

        server_constant_resource_set = [(HGate(), ri['h'] ),
                               (CZGate(), ri['cz']),
                               ]
        
        ubqc = QuantumCircuit(self.constant_compute_space, name='ubqc')
        for gate, qubits in server_constant_resource_set:
            ubqc.append(gate, qubits)
        ubqc.to_instruction()

        return BOP('compute', tuple(range(self.constant_compute_space)), [], ubqc, gate_seq=gate_seq)
    
    def _server_recursive_resource_set(self, gate_seq, k_for_theta):
        '''
        Creates server gate circuit.

        Args:
            gate_seq: int - used to store the information of which gate from original circuit, this translation is coming from.
            theta: float - contain the theta parameter (in radian) to apply theta rotation on the circuit. (Default = 2pi)

        Return:
            BOP - BOP class with modified conditional
            for better visualization Tuple[BOP] can also be used.

        Raise: 
            None
            
        Library Dependency:
            qiskit.circuit.library  - HGate, CXGate, CZGate, CCXGate, RZGate, TGate
            qiskit - QuantumCircuit
            math - pi
        '''
        from qiskit.circuit.library import HGate, CXGate, CZGate, CCXGate, RZGate, TGate
        from qiskit import QuantumCircuit
        from math import pi

        ri = self.ri

        server_recursive_resource_set = [(RZGate(pi/2**(k_for_theta)), ri['rz'])]
        
        ubqc = QuantumCircuit(self.constant_compute_space, name=f'ubqc_pi/{2**(k_for_theta)}')
        for gate, qubits in server_recursive_resource_set:
            ubqc.append(gate, qubits)
        ubqc.to_instruction()

        return BOP('compute', tuple(range(self.constant_compute_space)), [], ubqc, gate_seq=gate_seq)


