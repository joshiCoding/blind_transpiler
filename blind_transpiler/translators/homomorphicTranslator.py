from math import pi
from ..essentials.bop import BOP
from .base import BaseTranslator
from ..global_value_store import GlobalVariablesAndFunctions

# class StandardBlindTranslation(BaseTranslator):
class HomomorphicTranslation(BaseTranslator):
    def __init__(self):
        '''        
        Implementation is based on paper "Joshi, Mohit, Manoj Kumar Mishra, and S. Karthikeyan. "Quantum computing on encrypted data with arbitrary rotation gates." arXiv preprint arXiv:2508.18811 (2025)."

        Rightnow, this function have no use, made to remain consistent with other classes and for unseen future needs.
        The return type of each function is tuple of class BOP and the length is variable.


        '''
        GVF = GlobalVariablesAndFunctions()

        self.constant_compute_space = GVF.qhe_compute_space   # Note: This space can be reduce to 9 as rz can perform s,t gate also.
        self.ri = {'rz':(0,)}  # resource_index: index of resource in server. Note, all other gates do not require additional ancilla space
        self.M = GVF.M

        None


    def h(self, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 'h' gate for qhe.
        Needed size of encryption key = 2

        Args:
            key (list[int]):
                contains randomly generated binary keys, each element can be 0 or 1.
            qargs (list[int]):
                contains the argument on which the key has to be applied.
            gate_seq (int):
                used to store the information of which gate from original circuit, this translation is coming from.

        Returns:
            Tuple[BOP]: 
                tuple of BOP class object sequence needed for encryption, compute and decryption of the h gate.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library:
                XGate, ZGate, HGate

        '''
        from qiskit.circuit.library import XGate, ZGate, HGate

        q = self._create_qubit_map(qargs)

        A,B = key

        enc_1 = BOP('enc', (q[0],), [] , XGate(), A, gate_seq=gate_seq)
        enc_2 = BOP('enc', (q[0],), [], ZGate(),B, gate_seq=gate_seq)

        compute =  self._server_resource( q, 'h', gate_seq, theta=None)

        dec_1 = BOP('dec', (q[0],), [],  XGate(),B, gate_seq=gate_seq)
        dec_2 = BOP('dec',(q[0],), [], ZGate(), A, gate_seq=gate_seq)

        return (enc_1, enc_2, *compute, dec_1, dec_2)

    def s(self, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 's' gate for qhe.
        Needed size of encryption key = 2

        Args:
            key (list[int]) 
                contains randomly generated binary keys, each element can be 0 or 1.
            qargs (list[int]) 
                contains the argument on which the key has to be applied.
            gate_seq (int) 
                used to store the information of which gate from original circuit, this translation is coming from.

        Return:
            Tuple[BOP]: 
                tuple of BOP class object sequence needed for encryption, compute and decryption of the s gate.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library: 
                XGate, ZGate, RZGate
            math: 
                pi

        '''
        from qiskit.circuit.library import XGate, ZGate, RZGate
        from math import pi

        q = self._create_qubit_map(qargs)
        A,B = key

        enc_1 = BOP('enc', (q[0],), [],  XGate(), A, gate_seq=gate_seq)
        enc_2 = BOP('enc', (q[0],), [],  ZGate(), B, gate_seq=gate_seq) 

        compute =  self._server_resource( q, 's', gate_seq, theta=None)

        dec_1 = BOP('dec', (q[0],), [],  ZGate(), A^B, gate_seq=gate_seq)
        dec_2 = BOP('dec', (q[0],), [],  XGate(), A, gate_seq=gate_seq)

        return (enc_1, enc_2, *compute, dec_1, dec_2)

    def sdg(self, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 'sdg' gate for qhe.
        Needed size of encryption key = 2

        Args:
            key (list[int]) 
                contains randomly generated binary keys, each element can be 0 or 1.
            qargs (list[int]) 
                contains the argument on which the key has to be applied.
            gate_seq (int) 
                used to store the information of which gate from original circuit, this translation is coming from.

        Return:
            Tuple[BOP]: 
                tuple of BOP class object sequence needed for encryption, compute and decryption of the sdg gate.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library: 
                XGate, ZGate, RZGate
            math: 
                pi

        '''
        from qiskit.circuit.library import XGate, ZGate, RZGate
        from math import pi

        q = self._create_qubit_map(qargs)
        A,B = key

        enc_1 = BOP('enc', (q[0],), [],  XGate(), A, gate_seq=gate_seq)
        enc_2 = BOP('enc', (q[0],), [],  ZGate(), B, gate_seq=gate_seq) 

        compute =  self._server_resource( q, 'sdg', gate_seq, theta=None)

        dec_1 = BOP('dec', (q[0],), [],  ZGate(), A^B, gate_seq=gate_seq)
        dec_2 = BOP('dec', (q[0],), [],  XGate(), A, gate_seq=gate_seq)

        return (enc_1, enc_2, *compute, dec_1, dec_2)

    def t(self, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 't' gate for qhe.
        Needed size of encryption key = 4

        Args:
            key (list[int]): 
                contains randomly generated binary keys, each element can be 0 or 1.
            qargs (list[int]): 
                contains the argument on which the key has to be applied.
            gate_seq (int): 
                used to store the information of which gate from original circuit, this translation is coming from.

        Return:
            Tuple[BOP]: 
                tuple of BOP class object sequence needed for encryption, compute and decryption of the 't' gate.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library: 
                XGate, ZGate, RZGate
            math:  
                pi

        '''
        from qiskit.circuit.library import XGate, ZGate, IGate
        from math import pi

        q = self._create_qubit_map(qargs)
        A,B, A1,B1 = key

        enc_1 = BOP('enc', (q[0],), [],  XGate(), A, gate_seq=gate_seq)
        enc_2 = BOP('enc', (q[0],), [],  ZGate(), B, gate_seq=gate_seq) 

        # compute = BOP('compute', (q[0],), [],  RZGate(pi/4), gate_seq=gate_seq)
        compute =  self._server_resource( q, 't', gate_seq, theta=None)

        dec_1 = BOP('dec', (q[0],), [],  ZGate(), B, gate_seq=gate_seq)
        dec_2 = BOP('dec', (q[0],), [],  XGate(), A, gate_seq=gate_seq)

        if A == 1:
            s_compute =  self.s( key=[A1, B1], qargs=qargs, gate_seq=gate_seq)
        else:
            s_compute = [BOP('client', (q[0],), [],  IGate(), A, gate_seq=gate_seq) for _ in range(5)] # done to make the length of callback same when used in fdqc library


        return (enc_1, enc_2, *compute,  dec_1, dec_2, *s_compute)

    def tdg(self, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 't' gate for qhe.
        Needed size of encryption key = 4

        Args:
            key (list[int]): 
                contains randomly generated binary keys, each element can be 0 or 1.
            qargs (list[int]): 
                contains the argument on which the key has to be applied.
            gate_seq (int): 
                used to store the information of which gate from original circuit, this translation is coming from.

        Return:
            Tuple[BOP]: 
                tuple of BOP class object sequence needed for encryption, compute and decryption of the 't' gate.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library: 
                XGate, ZGate, RZGate
            math:  
                pi

        '''
        from qiskit.circuit.library import XGate, ZGate, IGate
        from math import pi

        q = self._create_qubit_map(qargs)
        A,B, A1,B1 = key

        enc_1 = BOP('enc', (q[0],), [],  XGate(), A, gate_seq=gate_seq)
        enc_2 = BOP('enc', (q[0],), [],  ZGate(), B, gate_seq=gate_seq) 

        # compute = BOP('compute', (q[0],), [],  RZGate(pi/4), gate_seq=gate_seq)
        compute =  self._server_resource( q, 'tdg', gate_seq, theta=None)

        dec_1 = BOP('dec', (q[0],), [],  ZGate(), B, gate_seq=gate_seq)
        dec_2 = BOP('dec', (q[0],), [],  XGate(), A, gate_seq=gate_seq)


        if A == 1:
            sdg_compute =  self.sdg( key=[A1, B1], qargs=qargs, gate_seq=gate_seq)
        else:
            sdg_compute = [BOP('client', (q[0],), [],  IGate(), A, gate_seq=gate_seq) for _ in range(5)] # done to make the length of callback same when used in fdqc library


        return (enc_1, enc_2, *compute,  dec_1, dec_2, *sdg_compute)


    def rz(self, theta, key, qargs, gate_seq):
        '''
        Encryption and Decryption logic for 'rz' gate of qhe. (Can't handle different keys for all the gates rightnow.)
        Decomposes the theta in integral power of series = a*pi + b*pi/2 + c*pi/4 + d*pi/8 + e*pi/16 + ..... (default= 20 precision points) approximatedly equal to theta, if theta is not integer power of pi/4, using function '_rz_integral'
        Logic of the function:
        
            * Case 1: exact expansion for n*pi/4 if n is integer.
            * Case 2: approximate expansion if n is not integer.

        Args:
            theta: float contain the theta parameter (in radian) to apply theta rotation on the circuit.
            key: list[int] contains randomly generated binary keys, each element can be 0 or 1.
            qargs: list[int] contains the argument on which the key has to be applied.
            gate_seq: int used to store the information of which gate from original circuit, this translation is coming from.

        Return:
            Tuple[BOP] tuple of BOP class object sequence needed for encryption, compute and decryption of the s gate. Here as the circuit was of variable length, we have used recursive_roll to revert the output.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library XGate, ZGate, RZGate
            math  pi
        

        '''
        ## NOTE: function based on my paper 'quantum computing on encrypted data with arbitrary rotation gates'
        ## check the correctness here
        from qiskit.circuit.library import SwapGate, XGate, ZGate
        from math import ceil, pi,log # remove this line after testing

        ri = self.ri
        qargs = self._create_qubit_map(qargs)

        bin, int_part =self._decompose_theta(theta)  # precision can also be asked from user


        x_key = [key[i] for i in range(len(key)) if i % 2 == 0]
        z_key = [key[i] for i in range(len(key)) if i % 2 != 0]

        full_variable_unroll = []

        M = len(bin)

        # handle integral part
        if int_part % 2 == 1:
            full_variable_unroll.append(BOP('client', (qargs[0],), [],  ZGate(), 1, gate_seq=gate_seq))   

        # pad the bin to make it run for bin[M]
        bin.insert(0,0)         


        for m in range(M, 0,-1):
            if bin[m] == 0:
                pass # no need to do anything if angle is not present
                # this logic is written just for clarity
            if bin[m] == 1 or bin[m]==-1:
                run_of_one = False
                cond = 1 if bin[m] == 1 or bin[m] == -1 else 0
                full_variable_unroll.append(BOP('enc', (qargs[0],), [],  XGate(), x_key[m], gate_seq=gate_seq))
                full_variable_unroll.append(BOP('enc', (qargs[0],), [],  ZGate(), z_key[m], gate_seq=gate_seq))
                full_variable_unroll.append(BOP('swap', (qargs[0],ri['rz'][0]), [], SwapGate(), cond, gate_seq=gate_seq ))
                full_variable_unroll.append(*self._server_resource( qargs, 'rz', gate_seq, theta=bin[m]*pi/2**m))
                full_variable_unroll.append(BOP('swap', (qargs[0],ri['rz'][0]), [], SwapGate(), cond ,gate_seq=gate_seq ))
                full_variable_unroll.append(BOP('dec', (qargs[0],), [],  ZGate(), z_key[m], gate_seq=gate_seq))
                full_variable_unroll.append(BOP('dec', (qargs[0],), [],  XGate(), x_key[m], gate_seq=gate_seq))
                if (x_key[m]) == 1:
                    run_of_one = True

                # for recursive correction of 2\theta  
                for k in range(m-1, 0, -1 ):
                    if run_of_one == True:
                        cond = x_key[k+1]
                        full_variable_unroll.append(BOP('enc', (qargs[0],), [],  XGate(), x_key[k], gate_seq=gate_seq))
                        full_variable_unroll.append(BOP('enc', (qargs[0],), [],  ZGate(), z_key[k], gate_seq=gate_seq))
                        full_variable_unroll.append(BOP('swap', (qargs[0],ri['rz'][0]), [], SwapGate(), cond ,gate_seq=gate_seq ))
                        full_variable_unroll.append(*self._server_resource( qargs, 'rz', gate_seq, theta=bin[m]*pi/2**k))
                        full_variable_unroll.append(BOP('swap', (qargs[0],ri['rz'][0]), [], SwapGate(), cond,gate_seq=gate_seq ))
                        full_variable_unroll.append(BOP('dec', (qargs[0],), [],  ZGate(), z_key[k], gate_seq=gate_seq))
                        full_variable_unroll.append(BOP('dec', (qargs[0],), [],  XGate(), x_key[k], gate_seq=gate_seq))
                        if (x_key[k]) == 0:
                            run_of_one = False 

                    if run_of_one == False:
                        full_variable_unroll.append(BOP('enc', (qargs[0],), [],  XGate(), x_key[k], gate_seq=gate_seq))
                        full_variable_unroll.append(BOP('enc', (qargs[0],), [],  ZGate(), z_key[k], gate_seq=gate_seq))
                        full_variable_unroll.append(*self._server_resource( qargs, 'rz', gate_seq, theta=bin[m]*pi/2**k))
                        full_variable_unroll.append(BOP('dec', (qargs[0],), [],  ZGate(), z_key[k], gate_seq=gate_seq))
                        full_variable_unroll.append(BOP('dec', (qargs[0],), [],  XGate(), x_key[k], gate_seq=gate_seq))
                
                # last Z correction
                if run_of_one == True:
                    cond = 1 if bin[m] == 1 or bin[m] == -1 else 0
                    full_variable_unroll.append(BOP('client', (qargs[0],), [],  ZGate(), cond, gate_seq=gate_seq))



        return tuple(full_variable_unroll)


    



    def cx(self, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 'cx' gate for qhe.
        Needed size of encryption key = 4

        Args:
            key: list[int] contains randomly generated binary keys, each element can be 0 or 1.
            qargs: list[int] contains the argument on which the key has to be applied.
            gate_seq: int used to store the information of which gate from original circuit, this translation is coming from.

        Return:
            Tuple[BOP] tuple of BOP class object sequence needed for encryption, compute and decryption of the 'cx' gate.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library XGate, ZGate
            math  - pi

        '''
        from qiskit.circuit.library import XGate, ZGate

        q = self._create_qubit_map(qargs)
        A,B,C,D = key
 

        enc_1 = BOP('enc', (q[0],), [],  XGate(), A, gate_seq=gate_seq)
        enc_2 = BOP('enc', (q[0],), [],  ZGate(), B, gate_seq=gate_seq) 

        enc_3 = BOP('enc', (q[1],), [],  XGate(), C, gate_seq=gate_seq)
        enc_4 = BOP('enc', (q[1],), [],  ZGate(), D, gate_seq=gate_seq) 

        compute =  self._server_resource( q, 'cx', gate_seq, theta=None)

        dec_1 = BOP('dec', (q[0],), [],  ZGate(), B^D, gate_seq=gate_seq)
        dec_2 = BOP('dec', (q[0],), [],  XGate(), A, gate_seq=gate_seq )
        
        dec_3 =BOP('dec', (q[1],), [],  ZGate(), D, gate_seq=gate_seq)
        dec_4 = BOP('dec', (q[1],), [],  XGate(), A^C, gate_seq=gate_seq)


        return (enc_1, enc_2, enc_3, enc_4, *compute, dec_1, dec_2, dec_3, dec_4)

        

    def cz(self, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 'cz' gate for qhe.
        Needed size of encryption key = 4

        Args:
            key: list[int] contains randomly generated binary keys, each element can be 0 or 1.
            qargs: list[int] contains the argument on which the key has to be applied.
            gate_seq: int used to store the information of which gate from original circuit, this translation is coming from.

        Return:
            Tuple[BOP] tuple of BOP class object sequence needed for encryption, compute and decryption of the 'cz' gate.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library - XGate, ZGate
            math  - pi

        '''
        from qiskit.circuit.library import XGate, ZGate
        q = self._create_qubit_map(qargs)
        A,B,C,D = key
        # a,b,c,d = key

        enc_1 = BOP('enc', (q[0],), [],  XGate(), A, gate_seq=gate_seq)
        enc_2 = BOP('enc', (q[0],), [],  ZGate(), B, gate_seq=gate_seq) 

        enc_3 = BOP('enc', (q[1],), [],  XGate(), C, gate_seq=gate_seq)
        enc_4 = BOP('enc', (q[1],), [],  ZGate(), D, gate_seq=gate_seq) 

        compute =  self._server_resource( q, 'cz', gate_seq, theta=None)

        dec_1 = BOP('dec', (q[0],), [],  ZGate(), B^C, gate_seq=gate_seq)
        dec_2 = BOP('dec', (q[0],), [],  XGate(), A, gate_seq=gate_seq)

        dec_3 = BOP('dec', (q[1],), [],  ZGate(), A^D, gate_seq=gate_seq)    
        dec_4 = BOP('dec', (q[1],), [],  XGate(), C, gate_seq=gate_seq)

        return (enc_1, enc_2, enc_3, enc_4, *compute, dec_1, dec_2, dec_3, dec_4)



    def ccx(self, key, qargs,  gate_seq):
        '''
        Encryption and decryption logic of 't' gate for qhe.
        Needed size of encryption key = 18 (Need hidden conditionals for decryption: 1 CZ and 2 CX = 6 + 1*4 + 2*4 = 18)

        Args:
            key: list[int] contains randomly generated binary keys, each element can be 0 or 1.
            qargs: list[int] contains the argument on which the key has to be applied.
            gate_seq: int used to store the information of which gate from original circuit, this translation is coming from.

        Return:
            Tuple[BOP] tuple of BOP class object sequence needed for encryption, compute and decryption of the 't' gate.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library - XGate, ZGate
            math  - pi

        '''
        from qiskit.circuit.library import XGate, ZGate

        q = self._create_qubit_map(qargs)
        A,B,C,D,E,F,   G,H,I,J,    K,L,M,N,  O,P,Q,R = key

        enc_1 = BOP('enc', (q[0],), [],  XGate(), A, gate_seq=gate_seq)
        enc_2 = BOP('enc', (q[0],), [],  ZGate(), B, gate_seq=gate_seq) 

        enc_3 = BOP('enc', (q[1],), [],  XGate(), C, gate_seq=gate_seq)
        enc_4 = BOP('enc', (q[1],), [],  ZGate(), D, gate_seq=gate_seq) 

        enc_5 = BOP('enc', (q[2],), [],  XGate(), E, gate_seq=gate_seq)
        enc_6 = BOP('enc', (q[2],), [],  ZGate(), F, gate_seq=gate_seq)

        compute =  self._server_resource( q, 'ccx', gate_seq, theta=None)

        dec_1 = BOP('dec', (q[2],), [],  ZGate(), F, gate_seq=gate_seq)
        dec_2 = BOP('dec', (q[2],), [],  XGate(), E, gate_seq=gate_seq)

        #apply conditional cz
        cz_enc_1, cz_enc_2, cz_enc_3, cz_enc_4, cz_compute, cz_dec_1, cz_dec_2, cz_dec_3, cz_dec_4 = self._apply_conditional(F,  self.cz((G,H,I,J), (q[0],q[1]), gate_seq=gate_seq))


        dec_4 = BOP('dec', (q[1],), [],  ZGate(), D, gate_seq=gate_seq)
        dec_5 = BOP('dec', (q[1],), [], XGate(), C, gate_seq=gate_seq)

        #apply first conditional cx
        cx1_enc_1, cx1_enc_2, cx1_enc_3, cx1_enc_4, cx1_compute, cx1_dec_1, cx1_dec_2, cx1_dec_3, cx1_dec_4 = self._apply_conditional(C,  self.cx((K,L,M,N), (q[0],q[2]),  gate_seq=gate_seq))


        dec_6 = BOP('dec',(q[0],), [],  ZGate(), B, gate_seq=gate_seq)
        dec_7 = BOP('dec', (q[0],), [],  XGate(), A, gate_seq=gate_seq)

        #apply second conditional cx
        cx2_enc_1, cx2_enc_2, cx2_enc_3, cx2_enc_4, cx2_compute, cx2_dec_1, cx2_dec_2, cx2_dec_3, cx2_dec_4 = self._apply_conditional(A, self.cx((O,P,Q,R),(q[1],q[2]),  gate_seq=gate_seq))


        return (enc_1, enc_2, enc_3, enc_4, enc_5, enc_6,
                *compute,
                dec_1, dec_2, 
                cz_enc_1, cz_enc_2, cz_enc_3, cz_enc_4, cz_compute, cz_dec_1, cz_dec_2, cz_dec_3, cz_dec_4,
                dec_4, dec_5,
                cx1_enc_1, cx1_enc_2, cx1_enc_3, cx1_enc_4, cx1_compute, cx1_dec_1, cx1_dec_2, cx1_dec_3, cx1_dec_4,
                dec_6, dec_7,
                cx2_enc_1, cx2_enc_2, cx2_enc_3, cx2_enc_4, cx2_compute, cx2_dec_1, cx2_dec_2, cx2_dec_3, cx2_dec_4 
                )
    

    # utility functions
    def _apply_conditional(self, x, op_tuple):
        '''
        Modifies the conditional of the list of object of BOP class, with Binary ANDing it with incoming x, using the 'conditional_and' function of BOP class.

        Args:
            x ({0,1}):
                conditional to be used for conditional applying gate like cx and cz in ccx decryption
            op_tuple (tuple[BOP]): 
                list of object of BOP class to change the conditional

        Return:
            tuple[BOP]
                Tuple of object of BOP class with modified conditional

        Raise: 
            None
            
        Library Dependency:
            None
        '''
        lst = []
        for op in op_tuple:
            new_op = op.conditional_and(x)
            lst.append(new_op)

        return tuple(lst)
    
    def _create_qubit_map(self, new_qargs):
        '''
        Creates a map between old and new qargs to be used for update the position of operation.
        This is used if place like cx(1,2) has to applies but library is made such that it implements cx(0,1), this function ensures hassle-free proper translation.

        Args:
            new_qargs (List[int]):
                store new qubit position, according to above example store [1,2]

        Returns:
            Dict[int->int]:
                dictionary map of old_qubit->new_qubit

        Raise: 
            None
            
        Library Dependency:
            None

        '''
        qarg_map = {}
        for i, qargs in enumerate(new_qargs):
            qarg_map[i] = qargs
        return qarg_map

    def _server_resource(self, q, gate, gate_seq, theta=None):
        '''
        Defines the server resource whict take in gate and apply it on demand

        Args:
            q: list of qubit locations
            gate: the gate that is needed to be implemented
            gate_seq: the sequence for which the gate is being implemented
            theta: additional argument need to implementation of Rz gate only

        Return:
            unroll: tuple that contains the gates that have been implemented by server
        
        Raise:
            ValueError('Internal Error: no theta found.')
            Raises error if theta is not gate but gate=Rz which requires theta

        '''

        from qiskit.circuit.library import HGate, RZGate, CXGate, CZGate, CCXGate

        unroll = []
        if gate == 'h':
            unroll.append(BOP('compute', (q[0],), [], HGate(), gate_seq=gate_seq))
        elif gate == 's':
            unroll.append(BOP('compute', (q[0],), [],  RZGate(pi/2), gate_seq=gate_seq))
        elif gate == 'sdg':
            unroll.append(BOP('compute', (q[0],), [],  RZGate(-pi/2), gate_seq=gate_seq))
        elif gate == 't':
            unroll.append(BOP('compute', (q[0],), [],  RZGate(pi/4), gate_seq=gate_seq))
        elif gate == 'tdg':
            unroll.append(BOP('compute', (q[0],), [],  RZGate(-pi/4), gate_seq=gate_seq))
        elif gate == 'rz':
            if theta == None: raise ValueError('Internal Error: no theta found.')
            unroll.append(BOP('compute', self.ri['rz'], [], RZGate(theta), gate_seq=gate_seq))
        elif gate == 'cx':
            unroll.append(BOP('compute', (q[0],q[1]), [],  CXGate(), gate_seq=gate_seq))
        elif gate == 'cz':
            unroll.append(BOP('compute', (q[0],q[1]), [],  CZGate(), gate_seq=gate_seq))
        elif gate == 'ccx':
            unroll.append(BOP('compute', (q[0],q[1],q[2]), [],  CCXGate(), gate_seq=gate_seq) )
        
        return tuple(unroll)
