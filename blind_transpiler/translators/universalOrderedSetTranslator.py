from math import pi
from ..essentials.bop import BOP
from .base import BaseTranslator
from .homomorphicTranslator import HomomorphicTranslation
from ..global_value_store import GlobalVariablesAndFunctions


# class FDQC(BaseTranslator):
class UniversalOrderedSetTranslator(BaseTranslator):
    """
    Library class implementing Full-Blind Quantum Computation (FDQC).

    Built on top of the HomomorphicTranslation class.
    Although inheritance from this class is possible,
    it may not always be desirable due to protocol-specific assumptions.

    The implementation is based on:

        Liu, Wen-Jie, et al.
        "Full-blind delegating private quantum computation."
        arXiv preprint arXiv:2002.00464 (2020).

    Notes:
        Assumes a constant compute space of 11 ancilla qubits.

        The resource set additionally includes the ``rz`` gate,
        which was not explicitly present in the original literature.
        This enables more practical universal computation.

        If the compute-space assumptions are modified here,
        corresponding updates should also be made to
        ``BQC.fdqc().constant_compute_space``.

    """
    def __init__(self):
        GVF = GlobalVariablesAndFunctions()

        self.constant_compute_space = GVF.fdqc_compute_space  # Note: This space can be reduce to 9 as rz can perform s,t gate also.
        self.ri = {'h':(0,), 's':(1,), 'cx':(2,3), 'cz':(4,5), 'ccx':(6,7,8), 'rz':(9,), 't': (10,)}  # resource_index: index of resource in server.


    def h(self, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 'h' gate for fdqc.
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
        from qiskit.circuit.library import  SwapGate

        ri = self.ri

        enc_1, enc_2, _ , dec_1, dec_2 = HomomorphicTranslation().h(key, qargs, gate_seq)
        swap = BOP('swap', (qargs[0],ri['h'][0]), [], SwapGate(), gate_seq=gate_seq )
        compute = self._server_resource_set(gate_seq=gate_seq)

        return (enc_1, enc_2, swap, compute, swap, dec_1, dec_2)
        
    def s(self, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 's' gate for fdqc.
        Needed size of encryption key = 2
        Different optimized way of running sdg = s.s.s = z.s (take 1 gates and keys = 2)


        Args:
            key: list[int] - contains randomly generated binary keys, each element can be 0 or 1.
            qargs: list[int] - contains the argument on which the key has to be applied.
            gate_seq: int - used to store the information of which gate from original circuit, this translation is coming from.

        Return:
            Tuple[BOP] - tuple of BOP class object sequence needed for encryption, compute and decryption of the 's' gate.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library - SwapGate

        '''
        from qiskit.circuit.library import SwapGate

        ri = self.ri

        enc_1, enc_2, _ , dec_1, dec_2 = HomomorphicTranslation().s(key, qargs, gate_seq)
        swap = BOP('swap', (qargs[0],ri['s'][0]), [], SwapGate(), gate_seq=gate_seq )
        compute = self._server_resource_set(gate_seq=gate_seq)

        return (enc_1, enc_2, swap, compute, swap, dec_1, dec_2)

    def sdg(self, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 's' gate for fdqc.
        Needed size of encryption key = 2*3 (no. of keys in s + times the s need to run (sdg = s^3))

        Args:
            key: list[int] - contains randomly generated binary keys, each element can be 0 or 1.
            qargs: list[int] - contains the argument on which the key has to be applied.
            gate_seq: int - used to store the information of which gate from original circuit, this translation is coming from.

        Return:
            Tuple[BOP] - tuple of BOP class object sequence needed for encryption, compute and decryption of the 's' gate.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library - SwapGate


        '''
        from qiskit.circuit.library import SwapGate, ZGate

        ri = self.ri

        unroll = []

        # optimized way
        unroll.append(BOP('client', (qargs[0],), [],  ZGate(), 1, gate_seq=gate_seq))
        unroll.extend([*self.s(key,qargs, gate_seq)])
        return tuple(unroll)
    
    def t(self, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 't' gate for fdqc.
        Needed size of encryption key = 4
        Note: has a temporary fix

        Args:
            key: list[int] - contains randomly generated binary keys, each element can be 0 or 1.
            qargs: list[int] - contains the argument on which the key has to be applied.
            gate_seq: int - used to store the information of which gate from original circuit, this translation is coming from.

        Return:
            Tuple[BOP] - tuple of BOP class object sequence needed for encryption, compute and decryption of the 't' gate.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library - SwapGate, IGate

        '''
        from qiskit.circuit.library import  SwapGate, IGate

        ri = self.ri


        enc_1, enc_2, _ , dec_1, dec_2, s_enc_1, s_enc_2, _ , s_dec_1, s_dec_2 = HomomorphicTranslation().t(key, qargs, gate_seq)

        A, _,_,_ = key
        swap = BOP('swap', (qargs[0],ri['t'][0]), [], SwapGate(), gate_seq=gate_seq )
        compute = self._server_resource_set(gate_seq=gate_seq)

        s_swap = BOP('swap', (qargs[0],ri['s'][0]), [], SwapGate(), A,  gate_seq=gate_seq )   # can also be optimized if key = 0
        s_compute = compute if A == 1 else BOP('client', (qargs[0],), [], IGate(), A, gate_seq=gate_seq )  # temporary fix

        return (enc_1, enc_2, 
                swap, compute, swap,  
                dec_1, dec_2,
                s_enc_1, s_enc_2, 
                s_swap, s_compute, s_swap, 
                s_dec_1, s_dec_2
                )


    def tdg(self, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 't' gate for fdqc.
        Needed size of encryption key = 4*7 (no. of keys in t + times the t need to run (tdg = t^7)).
        Different optimized way of running tdg = s.s.s.t = z.s.t (take 2 gates and keys = 2+4=6)

        Args:
            key: list[int] - contains randomly generated binary keys, each element can be 0 or 1.
            qargs: list[int] - contains the argument on which the key has to be applied.
            gate_seq: int - used to store the information of which gate from original circuit, this translation is coming from.

        Return:
            Tuple[BOP] - tuple of BOP class object sequence needed for encryption, compute and decryption of the 's' gate.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library - SwapGate

        '''
        from qiskit.circuit.library import SwapGate,ZGate

        ri = self.ri

        unroll = []

        unroll.append(BOP('client', (qargs[0],), [],  ZGate(), 1, gate_seq=gate_seq))
        unroll.extend([*self.s(key[0:2],qargs, gate_seq)])
        unroll.extend([*self.t(key[2:],qargs, gate_seq)])


        return tuple(unroll)



    def cx(self, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 'cx' gate for fdqc.
        Needed size of encryption key = 4

        Args:
            key: list[int] - contains randomly generated binary keys, each element can be 0 or 1.
            qargs: list[int] - contains the argument on which the key has to be applied.
            gate_seq: int - used to store the information of which gate from original circuit, this translation is coming from.

        Return:
            Tuple[BOP] - tuple of BOP class object sequence needed for encryption, compute and decryption of the 'cx' gate.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library - SwapGate

        '''
        from qiskit.circuit.library import SwapGate
        ri = self.ri


        enc_1, enc_2, enc_3, enc_4,  _ , dec_1, dec_2, dec_3, dec_4 = HomomorphicTranslation().cx(key, qargs, gate_seq)
        swap_1 = BOP('swap', (qargs[0],ri['cx'][0]), [], SwapGate(), gate_seq=gate_seq )
        swap_2 = BOP('swap', (qargs[1],ri['cx'][1]), [], SwapGate(), gate_seq=gate_seq )
        compute = self._server_resource_set(gate_seq=gate_seq)

        return (enc_1, enc_2, enc_3, enc_4, 
                swap_1, swap_2, compute, swap_1, swap_2, 
                dec_1, dec_2, dec_3, dec_4)


    def cz(self, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 'cz' gate for fdqc.
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
        from qiskit.circuit.library import SwapGate
        ri = self.ri

        enc_1, enc_2, enc_3, enc_4,  _ , dec_1, dec_2, dec_3, dec_4 = HomomorphicTranslation().cz(key, qargs, gate_seq)
        swap_1 = BOP('swap', (qargs[0],ri['cz'][0]), [], SwapGate(), gate_seq=gate_seq )
        swap_2 = BOP('swap', (qargs[1],ri['cz'][1]), [], SwapGate(), gate_seq=gate_seq )
        compute = self._server_resource_set(gate_seq=gate_seq)

        return (enc_1, enc_2, enc_3, enc_4, swap_1, swap_2, compute, swap_1, swap_2, dec_1, dec_2, dec_3, dec_4)

    def ccx(self, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 'ccx' gate for fdqc.
        Needed size of encryption key = 18

        Args:
            key: list[int] - contains randomly generated binary keys, each element can be 0 or 1.
            qargs: list[int] - contains the argument on which the key has to be applied.
            gate_seq: int - used to store the information of which gate from original circuit, this translation is coming from.

        Return:
            Tuple[BOP] - tuple of BOP class object sequence needed for encryption, compute and decryption of the 'ccx' gate.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library - SwapGate

        '''
        from qiskit.circuit.library import SwapGate, IGate
        ri = self.ri


        enc_1, enc_2, enc_3, enc_4, enc_5, enc_6, \
        _ , \
        dec_1, dec_2, \
        cz_enc_1, cz_enc2, cz_enc_3, cz_enc_4, _ , cz_dec_1, cz_dec_2, cz_dec_3, cz_dec_4,\
        dec_4, dec_5,\
        cx1_enc_1, cx1_enc2, cx1_enc_3, cx1_enc_4, _ , cx1_dec_1, cx1_dec_2, cx1_dec_3, cx1_dec_4,\
        dec_6, dec_7,\
        cx2_enc_1, cx2_enc2, cx2_enc_3, cx2_enc_4, _ , cx2_dec_1, cx2_dec_2, cx2_dec_3, cx2_dec_4  = HomomorphicTranslation().ccx(key, qargs, gate_seq)

        A,_,C,_,_,F, _,_,_,_,  _,_,_,_, _,_,_,_ = key      # keys are still needed to selectively apply swap and compute gates

        compute = self._server_resource_set(gate_seq=gate_seq)

        # swap for ccx gate
        swap_ccx_1 = BOP('swap', (qargs[0],ri['ccx'][0]), [], SwapGate(), gate_seq=gate_seq )
        swap_ccx_2 = BOP('swap', (qargs[1],ri['ccx'][1]), [], SwapGate(), gate_seq=gate_seq )
        swap_ccx_3 = BOP('swap', (qargs[2],ri['ccx'][2]), [], SwapGate(), gate_seq=gate_seq )

        # swap for cz gate apply only if F =1
        swap_cz_1 = BOP('swap', (qargs[0],ri['cz'][0]), [], SwapGate(), F, gate_seq=gate_seq )
        swap_cz_2 = BOP('swap', (qargs[1],ri['cz'][1]), [], SwapGate(), F, gate_seq=gate_seq )
        cz_compute = compute if F == 1 else BOP('client', (qargs[1],), [], IGate(), F, gate_seq=gate_seq )

        # swap for first cx gate, apply only if C =1
        swap_cx1_1 = BOP('swap', (qargs[0],ri['cx'][0]), [], SwapGate(), C, gate_seq=gate_seq )
        swap_cx1_2 = BOP('swap', (qargs[2],ri['cx'][1]), [], SwapGate(), C, gate_seq=gate_seq )
        cx1_compute = compute if C ==1 else BOP('client', (qargs[1],), [], IGate(), C,  gate_seq=gate_seq )

        # swap for second cx gate, apply only if A =1
        swap_cx2_1 = BOP('swap', (qargs[1],ri['cx'][0]), [], SwapGate(), A, gate_seq=gate_seq )
        swap_cx2_2 = BOP('swap', (qargs[2],ri['cx'][1]), [], SwapGate(), A, gate_seq=gate_seq )
        cx2_compute = compute if A ==1 else BOP('client', (qargs[1],), [], IGate(), A,  gate_seq=gate_seq )


        return (enc_1, enc_2, enc_3, enc_4, enc_5, enc_6,
                swap_ccx_1, swap_ccx_2, swap_ccx_3,
                compute,
                swap_ccx_1, swap_ccx_2, swap_ccx_3,
                dec_1, dec_2, 

                cz_enc_1, cz_enc2, cz_enc_3, cz_enc_4,
                swap_cz_1, swap_cz_2,
                cz_compute,   # cz on (0,1) qubit
                swap_cz_1, swap_cz_2,
                cz_dec_1, cz_dec_2, cz_dec_3, cz_dec_4,

                dec_4, dec_5,

                cx1_enc_1, cx1_enc2, cx1_enc_3, cx1_enc_4, 
                swap_cx1_1, swap_cx1_2,
                cx1_compute,  # cx on (0,2) qubit 
                swap_cx1_1, swap_cx1_2,
                cx1_dec_1, cx1_dec_2, cx1_dec_3, cx1_dec_4,

                dec_6, dec_7,

                cx2_enc_1, cx2_enc2, cx2_enc_3, cx2_enc_4, 
                swap_cx2_1, swap_cx2_2,
                cx2_compute, # cx on (1,2) qubit
                swap_cx2_1, swap_cx2_2,
                cx2_dec_1, cx2_dec_2, cx2_dec_3, cx2_dec_4 
                )
    

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

    def _server_resource_set(self, gate_seq,theta=2*pi):
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

        server_resource_set = [(HGate(), ri['h'] ),
                               (RZGate(pi/2), ri['s']),
                               (CXGate(), ri['cx']),
                               (CZGate(), ri['cz']),
                               (CCXGate(), ri['ccx']),
                               (RZGate(theta), ri['rz']),
                               (TGate(), ri['t'])]
        
        fdqc = QuantumCircuit(self.constant_compute_space, name='fdqc')
        for gate, qubits in server_resource_set:
            fdqc.append(gate, qubits)
        fdqc.to_instruction()

        return BOP('compute', tuple(range(self.constant_compute_space)), [], fdqc, gate_seq=gate_seq)

