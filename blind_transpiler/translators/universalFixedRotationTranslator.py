from math import pi
from ..essentials.bop import BOP
from .base import BaseTranslator

from functools import wraps


trap_flag = 1
full_angle = 4*pi
from .custom_gates.custom_gates import RZGate, RYGate, CRYGate, CRZGate, CCRYGate, CCRZGate
from qiskit.circuit.library import XGate, ZGate

def decompose_rotations_to_pi_over_4( func):
    from math import pi

    def _is_multiple_of(angle, base=pi/4, tol=1e-8):
        from math import isclose
        ratio = angle / base
        return isclose(ratio, round(ratio), abs_tol=tol)

    @wraps(func)
    def wrapper(*args, **kwargs):
        bops = func(*args, **kwargs)
        decomposed_bops = []

        for bop in bops:
            gate = bop.gate
            # Only decompose 'compute' and 'trap' rotations
            if len(gate.params) > 0 and bop.op_type in ['compute', 'trap'] and _is_multiple_of(gate.params[0]):
                angle = gate.params[0]

                steps = int(round(angle / (pi / 4)))
                for _ in range(abs(steps)):
                    modified_gate = gate.copy()
                    modified_gate.params = [pi/4]
                    
                    decomposed_bops.append(
                        bop.__class__(
                            op_type=bop.op_type,
                            qargs=bop.qargs,
                            cargs=bop.cargs,
                            gate=modified_gate,
                            conditional=bop.conditional,
                            gate_seq=bop.gate_seq
                        )
                    )
            else:
                decomposed_bops.append(bop)

        return tuple(decomposed_bops)
    return wrapper


class UniversalFixedRotationTranslator(BaseTranslator):
    '''
    Library class for Rotation based full-blind quantum computation.
    Logic is based on paper: 
    
        'Zhang, Xiaoqian, et al. "Single-server blind quantum computation with quantum circuit model." Quantum Information Processing 17 (2018): 1-18.'.

    NOTE: Following changes have been made from the original defined algorithm.
    complete angle of trap == 4pi (not 2pi as defined in the paper, which creates the phase interference in many algorithms)
    changes RZ gates to PhaseGate - due to difference of phase in implementation of these gates in qiskit 
    Also, note, if some future problems arise due to RY gate, they should also be changes to iRY() gates using PhaseGate(pi/2)


    Assumes variable compute space of 3*n ancilla qubits, where n is the no. of qubits in original circuit.


    '''
    def __init__(self):
        None 



    @decompose_rotations_to_pi_over_4 
    def h(self, key, qargs, gate_seq):
        """
        Encryption and decryption logic of 'h' gate for rotation-based fdqc.
        Needed size of encryption key = 6

        Args:
            key: list[int] - contains randomly generated binary keys, each element can be 0 or 1.
            qargs: list[int] - contains the argument on which the key has to be applied.
            gate_seq: int - used to store the information of which gate from original circuit, this translation is coming from.

        Return:
            Tuple[BOP] - tuple of BOP class object sequence needed for encryption, compute and decryption of the 'h' gate.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library - XGate, ZGate
            math - pi


        """

        q = self._create_qubit_map(qargs)

        A,B,C,D,E,F = key

        enc_1 = BOP('enc', (q[0],), [], XGate(), A, gate_seq=gate_seq)
        enc_2 = BOP('enc', (q[0],), [], ZGate(), B, gate_seq=gate_seq)

        enc_3 = BOP('enc', (q[1],), [], XGate(), C, gate_seq=gate_seq)
        enc_4 = BOP('enc', (q[1],), [], ZGate(), D, gate_seq=gate_seq)

        enc_5 = BOP('enc', (q[2],), [], XGate(), E, gate_seq=gate_seq)
        enc_6 = BOP('enc', (q[2],), [], ZGate(), F, gate_seq=gate_seq)

        compute_1 = BOP('compute', (q[0],), [], RZGate(pi), 1, gate_seq=gate_seq)
        compute_2 = BOP('compute', (q[0],), [], RYGate(pi/2), 1,gate_seq=gate_seq)


        trap_1 = BOP('trap', (q[1],q[2]), [], CRZGate(full_angle), trap_flag,  gate_seq=gate_seq)
        trap_2 = BOP('trap', (q[0],q[1],q[2]), [], CCRYGate(full_angle),trap_flag, gate_seq=gate_seq)
        trap_3 = BOP('trap', (q[0],q[1]), [], CRYGate(full_angle),trap_flag, gate_seq=gate_seq)   
        trap_4 = BOP('trap', (q[0],q[1],q[2]), [], CCRZGate(full_angle),trap_flag, gate_seq=gate_seq)


        dec_1 = BOP('dec', (q[0],), [], XGate(),B, gate_seq=gate_seq)
        dec_2 = BOP('dec',(q[0],), [], ZGate(), A, gate_seq=gate_seq)

        # to restore original
        dec_3 = BOP('enc', (q[1],), [], ZGate(), D, gate_seq=gate_seq)
        dec_4 = BOP('enc', (q[1],), [], XGate(), C, gate_seq=gate_seq)

        dec_5 = BOP('enc', (q[2],), [], ZGate(), F, gate_seq=gate_seq)
        dec_6 = BOP('enc', (q[2],), [], XGate(), E, gate_seq=gate_seq)

        return (enc_1, enc_2, enc_3, enc_4, enc_5, enc_6, compute_1, compute_2, trap_1, trap_2, trap_3, trap_4, dec_1, dec_2, dec_3, dec_4, dec_5, dec_6)
        
    @decompose_rotations_to_pi_over_4     
    def s(self, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 's' gate for rotation-based fdqc.
        Needed size of encryption key = 6

        Args:
            key: list[int] - contains randomly generated binary keys, each element can be 0 or 1.
            qargs: list[int] - contains the argument on which the key has to be applied.
            gate_seq: int - used to store the information of which gate from original circuit, this translation is coming from.

        Return:
            Tuple[BOP] - tuple of BOP class object sequence needed for encryption, compute and decryption of the 's' gate.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library - XGate, ZGate
            math - pi

        '''

        q = self._create_qubit_map(qargs)

        A,B,C,D,E,F = key

        enc_1 = BOP('enc', (q[0],), [], XGate(), A, gate_seq=gate_seq)
        enc_2 = BOP('enc', (q[0],), [], ZGate(), B, gate_seq=gate_seq)

        enc_3 = BOP('enc', (q[1],), [], XGate(), C, gate_seq=gate_seq)
        enc_4 = BOP('enc', (q[1],), [], ZGate(), D, gate_seq=gate_seq)

        enc_5 = BOP('enc', (q[2],), [], XGate(), E, gate_seq=gate_seq)
        enc_6 = BOP('enc', (q[2],), [], ZGate(), F, gate_seq=gate_seq)

        compute = BOP('compute', (q[0],), [], RZGate(pi/2), gate_seq=gate_seq)

        trap_1 = BOP('trap', (q[1],), [], RYGate(full_angle),trap_flag, gate_seq=gate_seq)
        trap_2 = BOP('trap', (q[0],q[1],q[2]), [], CCRYGate(full_angle), trap_flag,gate_seq=gate_seq)
        trap_3 = BOP('trap', (q[0],q[1]), [], CRZGate(full_angle),trap_flag, gate_seq=gate_seq)     
        trap_4 = BOP('trap', (q[0],q[1],q[2]), [], CCRZGate(full_angle),trap_flag, gate_seq=gate_seq)
        trap_5 = BOP('trap', (q[1],q[2]), [], CRYGate(full_angle),trap_flag, gate_seq=gate_seq)

        dec_1 = BOP('dec', (q[0],), [],  ZGate(), A^B, gate_seq=gate_seq)
        dec_2 = BOP('dec', (q[0],), [],  XGate(), A, gate_seq=gate_seq)


        # to restore original
        dec_3 = BOP('enc', (q[1],), [], ZGate(), D, gate_seq=gate_seq)
        dec_4 = BOP('enc', (q[1],), [], XGate(), C, gate_seq=gate_seq)

        dec_5 = BOP('enc', (q[2],), [], ZGate(), F, gate_seq=gate_seq)
        dec_6 = BOP('enc', (q[2],), [], XGate(), E, gate_seq=gate_seq)

        return (enc_1, enc_2, enc_3, enc_4, enc_5, enc_6, 
                compute,
                trap_1, trap_2, trap_3, trap_4, trap_5, 
                dec_1, dec_2, dec_3, dec_4, dec_5, dec_6)

    @decompose_rotations_to_pi_over_4 
    def sdg(self, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 's' gate for fdqc.
        Needed size of encryption key = 6*3 (no. of keys in s + times the s need to run (sdg = s^3)).
        Different optimized way of running sdg = s.s.s = z.s (take 1 gates and keys = 6)

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
        unroll = []

        ## optimized way
        unroll.append(BOP('client', (qargs[0],), [],  ZGate(), 1, gate_seq=gate_seq))
        unroll.extend([*self.s(key[0:],qargs, gate_seq)])

        return tuple(unroll)

    @decompose_rotations_to_pi_over_4     
    def t(self, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 't' gate for rotation-based fdqc.
        Needed size of encryption key = 8

        Args:
            key: list[int] - contains randomly generated binary keys, each element can be 0 or 1.
            qargs: list[int] - contains the argument on which the key has to be applied.
            gate_seq: int - used to store the information of which gate from original circuit, this translation is coming from.

        Return:
            Tuple[BOP] - tuple of BOP class object sequence needed for encryption, compute and decryption of the 't' gate.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library - XGate, ZGate
            math - pi

        '''
        q = self._create_qubit_map(qargs)

        A,B,C,D,E,F,  A1,B1 = key

        enc_1 = BOP('enc', (q[0],), [], XGate(), A, gate_seq=gate_seq)
        enc_2 = BOP('enc', (q[0],), [], ZGate(), B, gate_seq=gate_seq)

        enc_3 = BOP('enc', (q[1],), [], XGate(), C, gate_seq=gate_seq)
        enc_4 = BOP('enc', (q[1],), [], ZGate(), D, gate_seq=gate_seq)

        enc_5 = BOP('enc', (q[2],), [], XGate(), E, gate_seq=gate_seq)
        enc_6 = BOP('enc', (q[2],), [], ZGate(), F, gate_seq=gate_seq)

        compute = BOP('compute', (q[0],), [], RZGate(pi/4), gate_seq=gate_seq)

        # applying correction S gate
        s_enc_1 = BOP('enc', (q[0],), [], XGate(), A1 & A, gate_seq=gate_seq)
        s_enc_2 = BOP('enc', (q[0],), [], ZGate(), B1 & A, gate_seq=gate_seq)

        s_compute = BOP('compute', (q[0],), [], RZGate(pi/2), A ,gate_seq=gate_seq)

        s_dec_1 = BOP('dec', (q[0],), [], XGate(), A1 & A, gate_seq=gate_seq)    # note: order is reverse from original decryption of S gate
        s_dec_2 = BOP('dec', (q[0],), [], ZGate(), (A1^B1) & A, gate_seq=gate_seq)    # dec_1 = s_dec_2 and vice versa


        trap_1 = BOP('trap', (q[1],), [], RYGate(full_angle), trap_flag, gate_seq=gate_seq)
        trap_2 = BOP('trap', (q[1],q[2]), [], CRZGate(full_angle),trap_flag, gate_seq=gate_seq)
        trap_3 = BOP('trap', (q[1],q[2]), [], CRYGate(full_angle),trap_flag, gate_seq=gate_seq)
        trap_4 = BOP('trap', (q[0],q[1],q[2]), [], CCRYGate(full_angle),trap_flag, gate_seq=gate_seq)
        trap_5 = BOP('trap', (q[0],q[1],q[2]), [], CCRZGate(full_angle),trap_flag, gate_seq=gate_seq)


        dec_1 = BOP('dec', (q[0],), [], XGate(), A, gate_seq=gate_seq)
        dec_2 = BOP('dec', (q[0],), [], ZGate(), A^B, gate_seq=gate_seq)

        # to restore original
        dec_3 = BOP('enc', (q[1],), [], ZGate(), D, gate_seq=gate_seq)
        dec_4 = BOP('enc', (q[1],), [], XGate(), C, gate_seq=gate_seq)

        dec_5 = BOP('enc', (q[2],), [], ZGate(), F, gate_seq=gate_seq)
        dec_6 = BOP('enc', (q[2],), [], XGate(), E, gate_seq=gate_seq)

        return (enc_1, enc_2, enc_3, enc_4, enc_5, enc_6, compute, s_enc_1, s_enc_2, s_compute, s_dec_1, s_dec_2, trap_1, trap_2, trap_3, trap_4, trap_5, dec_1, dec_2, dec_3, dec_4, dec_5, dec_6)
    


    @decompose_rotations_to_pi_over_4     
    def tdg(self, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 't' gate for ssdqc.
        Needed size of encryption key = 8*7 (no. of keys in t + times the t need to run (tdg = t^7)).
        Different optimized way of running tdg = z.s.t (take 2 gates and keys = 6+8=14)

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
        unroll = []

        unroll.append(BOP('client', (qargs[0],), [],  ZGate(), 1, gate_seq=gate_seq))
        unroll.extend([*self.s(key[0:6],qargs, gate_seq)])
        unroll.extend([*self.t(key[6:],qargs, gate_seq)])


        return tuple(unroll)

    @decompose_rotations_to_pi_over_4 
    def cx(self, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 'cx' gate for rotation-based fdqc.
        Needed size of encryption key = 6

        Args:
            key: list[int] - contains randomly generated binary keys, each element can be 0 or 1.
            qargs: list[int] - contains the argument on which the key has to be applied.
            gate_seq: int - used to store the information of which gate from original circuit, this translation is coming from.

        Return:
            Tuple[BOP] - tuple of BOP class object sequence needed for encryption, compute and decryption of the 'cx' gate.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library - XGate, ZGate
            math - pi

        '''
        q = self._create_qubit_map(qargs)

        A,B,C,D,E,F = key

        enc_1 = BOP('enc', (q[0],), [], XGate(), A, gate_seq=gate_seq)
        enc_2 = BOP('enc', (q[0],), [], ZGate(), B, gate_seq=gate_seq)

        enc_3 = BOP('enc', (q[1],), [], XGate(), C, gate_seq=gate_seq)
        enc_4 = BOP('enc', (q[1],), [], ZGate(), D, gate_seq=gate_seq)

        enc_5 = BOP('enc', (q[2],), [], XGate(), E, gate_seq=gate_seq)
        enc_6 = BOP('enc', (q[2],), [], ZGate(), F, gate_seq=gate_seq)

        compute_1 = BOP('compute', (q[0],q[1]), [], CRZGate(pi), 1, gate_seq=gate_seq)
        compute_2 = BOP('compute', (q[0],q[1]), [], CRYGate(pi), gate_seq=gate_seq)

        trap_1 = BOP('trap', (q[0],), [], RYGate(full_angle), trap_flag, gate_seq=gate_seq)
        trap_2 = BOP('trap', (q[1],), [], RZGate(full_angle), trap_flag, gate_seq=gate_seq)
        trap_3 = BOP('trap', (q[0],q[1],q[2]), [], CCRYGate(full_angle), trap_flag, gate_seq=gate_seq)
        trap_4 = BOP('trap', (q[0],q[1],q[2]), [], CCRZGate(full_angle), trap_flag, gate_seq=gate_seq)

        dec_1 = BOP('dec', (q[0],), [], ZGate(), B^D, gate_seq=gate_seq)
        dec_2 = BOP('dec', (q[0],), [], XGate(), A, gate_seq=gate_seq )
        
        dec_3 =BOP('dec', (q[1],), [], ZGate(), D, gate_seq=gate_seq)
        dec_4 = BOP('dec', (q[1],), [], XGate(), A^C, gate_seq=gate_seq)

        dec_5 = BOP('enc', (q[2],), [], ZGate(), F, gate_seq=gate_seq)
        dec_6 = BOP('enc', (q[2],), [], XGate(), E, gate_seq=gate_seq)

        return (enc_1, enc_2, enc_3, enc_4, enc_5, enc_6, compute_1, compute_2, trap_1, trap_2, trap_3, trap_4, dec_1, dec_2, dec_3, dec_4, dec_5, dec_6)
    


    @decompose_rotations_to_pi_over_4 
    def cz(self, key,qargs, gate_seq):
        '''
        Encryption and decryption logic of 'cz' gate for rotation-based fdqc.
        Needed size of encryption key = 6

        Args:
            key: list[int] - contains randomly generated binary keys, each element can be 0 or 1.
            qargs: list[int] - contains the argument on which the key has to be applied.
            gate_seq: int - used to store the information of which gate from original circuit, this translation is coming from.

        Return:
            Tuple[BOP] - tuple of BOP class object sequence needed for encryption, compute and decryption of the 'cz' gate.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library - XGate, ZGate
            math - pi


        '''
        q = self._create_qubit_map(qargs)

        A,B,C,D,E,F = key

        enc_1 = BOP('enc', (q[0],), [], XGate(), A, gate_seq=gate_seq)
        enc_2 = BOP('enc', (q[0],), [], ZGate(), B, gate_seq=gate_seq)

        enc_3 = BOP('enc', (q[1],), [], XGate(), C, gate_seq=gate_seq)
        enc_4 = BOP('enc', (q[1],), [], ZGate(), D, gate_seq=gate_seq)

        enc_5 = BOP('enc', (q[2],), [], XGate(), E, gate_seq=gate_seq)
        enc_6 = BOP('enc', (q[2],), [], ZGate(), F, gate_seq=gate_seq)

        compute = BOP('compute', (q[0],q[1]), [], CRZGate(pi), gate_seq=gate_seq)    

        trap_1 = BOP('trap', (q[0],), [], RZGate(full_angle), trap_flag, gate_seq=gate_seq)
        trap_2 = BOP('trap', (q[1],q[2]), [], CRYGate(full_angle),trap_flag, gate_seq=gate_seq)     
        trap_3 = BOP('trap', (q[1],), [], RYGate(full_angle),trap_flag, gate_seq=gate_seq)
        trap_4 = BOP('trap', (q[0],q[1],q[2]), [], CCRYGate(full_angle),trap_flag, gate_seq=gate_seq) 
        trap_5 = BOP('trap', (q[0],q[1],q[2]), [], CCRZGate(full_angle),trap_flag, gate_seq=gate_seq) 

        dec_1 = BOP('dec', (q[0],), [], ZGate(), B^C, gate_seq=gate_seq)
        dec_2 = BOP('dec', (q[0],), [], XGate(), A, gate_seq=gate_seq)

        dec_3 = BOP('dec', (q[1],), [], ZGate(), A^D, gate_seq=gate_seq)
        dec_4 = BOP('dec', (q[1],), [], XGate(), C, gate_seq=gate_seq)

        dec_5 = BOP('enc', (q[2],), [], ZGate(), F, gate_seq=gate_seq)
        dec_6 = BOP('enc', (q[2],), [], XGate(), E, gate_seq=gate_seq)

        return (enc_1, enc_2, enc_3, enc_4, enc_5, enc_6, compute, trap_1, trap_2, trap_3, trap_4, trap_5, dec_1, dec_2, dec_3, dec_4, dec_5, dec_6)

    @decompose_rotations_to_pi_over_4 
    def ccx(self, key, qargs, gate_seq):
        '''
        Encryption and decryption logic of 'ccx' gate for rotation-based fdqc.
        Needed size of encryption key = 18: (Need hidden conditionals for decrypting one CZ and two CX = 6 + 1*4 + 2*4 = 18)


        Args:
            key: list[int] - contains randomly generated binary keys, each element can be 0 or 1.
            qargs: list[int] - contains the argument on which the key has to be applied.
            gate_seq: int - used to store the information of which gate from original circuit, this translation is coming from.

        Return:
            Tuple[BOP] - tuple of BOP class object sequence needed for encryption, compute and decryption of the 'ccx' gate.

        Raise: 
            None
            
        Library Dependency:
            qiksit.circuit.library - XGate, ZGate
            math - pi

        '''
        q = self._create_qubit_map(qargs)
        A,B,C,D,E,F,   A1,B1,C1,D1,    A2,B2,C2,D2,  A3,B3,C3,D3 = key

        enc_1 = BOP('enc', (q[0],), [], XGate(), A, gate_seq=gate_seq)
        enc_2 = BOP('enc', (q[0],), [], ZGate(), B, gate_seq=gate_seq) 

        enc_3 = BOP('enc', (q[1],), [], XGate(), C, gate_seq=gate_seq)
        enc_4 = BOP('enc', (q[1],), [], ZGate(), D, gate_seq=gate_seq) 

        enc_5 = BOP('enc', (q[2],), [], XGate(), E, gate_seq=gate_seq)
        enc_6 = BOP('enc', (q[2],), [], ZGate(), F, gate_seq=gate_seq)

        compute_1 = BOP('compute', (q[0],q[1],q[2]), [], CCRZGate(pi), 1, gate_seq=gate_seq) 
        compute_2 = BOP('compute', (q[0],q[1],q[2]), [], CCRYGate(pi), 1,  gate_seq=gate_seq) 

        dec_1 = BOP('dec', (q[2],), [], ZGate(), F, gate_seq=gate_seq)
        dec_2 = BOP('dec', (q[2],), [], XGate(), E, gate_seq=gate_seq)

        dec_4 = BOP('dec', (q[1],), [], ZGate(), D, gate_seq=gate_seq)
        dec_5 = BOP('dec', (q[1],), [], XGate(), C, gate_seq=gate_seq)

        dec_6 = BOP('dec',(q[0],), [], ZGate(), B, gate_seq=gate_seq)
        dec_7 = BOP('dec', (q[0],), [], XGate(), A, gate_seq=gate_seq)

        #apply conditional cz
        cz_enc_1 = BOP('enc', (q[0],), [], XGate(), A1 & F, gate_seq=gate_seq)
        cz_enc_2 = BOP('enc', (q[0],), [], ZGate(), B1 & F, gate_seq=gate_seq)

        cz_enc_3 = BOP('enc', (q[1],), [], XGate(), C1 & F, gate_seq=gate_seq)
        cz_enc_4 = BOP('enc', (q[1],), [], ZGate(), D1 & F, gate_seq=gate_seq)

        cz_compute = BOP('compute', (q[0],q[1]), [], CRZGate(pi), F, gate_seq=gate_seq) 

        cz_dec_1 = BOP('dec', (q[0],), [], ZGate(), (B1^C1) & F, gate_seq=gate_seq)
        cz_dec_2 = BOP('dec', (q[0],), [], XGate(), A1 & F, gate_seq=gate_seq)

        cz_dec_3 = BOP('dec', (q[1],), [], ZGate(), (A1^D1) & F, gate_seq=gate_seq)
        cz_dec_4 = BOP('dec', (q[1],), [], XGate(), C1 & F, gate_seq=gate_seq)


        trap_1 = BOP('trap', (q[0],), [], RZGate(full_angle),trap_flag, gate_seq=gate_seq)
        trap_2 = BOP('trap', (q[2],), [], RYGate(full_angle),trap_flag, gate_seq=gate_seq)
        trap_3 = BOP('trap', (q[0],q[1]), [], CRZGate(full_angle),trap_flag, gate_seq=gate_seq)
        trap_4 = BOP('trap', (q[1],q[2]), [], CRYGate(full_angle),trap_flag, gate_seq=gate_seq)

        #apply first conditional cx
        cx1_enc_1 = BOP('enc', (q[0],), [], XGate(), A2 & C, gate_seq=gate_seq)
        cx1_enc_2 = BOP('enc', (q[0],), [], ZGate(), B2 & C, gate_seq=gate_seq)

        cx1_enc_3 = BOP('enc', (q[2],), [], XGate(), C2 & C, gate_seq=gate_seq)
        cx1_enc_4 = BOP('enc', (q[2],), [], ZGate(), D2 & C, gate_seq=gate_seq)

        cx1_compute_1 = BOP('compute', (q[0],q[2]), [], CRZGate(pi), C, gate_seq=gate_seq) 
        cx1_compute_2 = BOP('compute', (q[0],q[2]), [], CRYGate(pi), C, gate_seq=gate_seq) 


        cx1_dec_1 = BOP('dec', (q[0],), [], ZGate(), (B2^D2) & C, gate_seq=gate_seq)
        cx1_dec_2 = BOP('dec', (q[0],), [], XGate(), A2 & C, gate_seq=gate_seq )
        
        cx1_dec_3 =BOP('dec', (q[2],), [], ZGate(), D2 & C, gate_seq=gate_seq)
        cx1_dec_4 = BOP('dec', (q[2],), [], XGate(), (A2^C2) & C, gate_seq=gate_seq)


        #apply second conditional cx
        cx2_enc_1 = BOP('enc', (q[1],), [], XGate(), A3 & A, gate_seq=gate_seq)
        cx2_enc_2 = BOP('enc', (q[1],), [], ZGate(), B3 & A, gate_seq=gate_seq)

        cx2_enc_3 = BOP('enc', (q[2],), [], XGate(), C3 & A, gate_seq=gate_seq)
        cx2_enc_4 = BOP('enc', (q[2],), [], ZGate(), D3 & A, gate_seq=gate_seq)

        cx2_compute_1 = BOP('compute', (q[1],q[2]), [], CRZGate(pi), A, gate_seq=gate_seq) 
        cx2_compute_2 = BOP('compute', (q[1],q[2]), [], CRYGate(pi), A, gate_seq=gate_seq) 

        cx2_dec_1 = BOP('dec', (q[1],), [], ZGate(), (B3^D3) & A, gate_seq=gate_seq)
        cx2_dec_2 = BOP('dec', (q[1],), [], XGate(), A3 & A, gate_seq=gate_seq )
        
        cx2_dec_3 =BOP('dec', (q[2],), [], ZGate(), D3 & A, gate_seq=gate_seq)
        cx2_dec_4 = BOP('dec', (q[2],), [], XGate(), (A3^C3) & A, gate_seq=gate_seq)


        return (enc_1, enc_2, enc_3, enc_4, enc_5, enc_6,
                compute_1,
                compute_2,
                dec_1, dec_2, 
                cz_enc_1, cz_enc_2, cz_enc_3, cz_enc_4, cz_compute, cz_dec_1, cz_dec_2, cz_dec_3, cz_dec_4,
                dec_4, dec_5,
                trap_1, trap_2, trap_3, trap_4,
                cx1_enc_1, cx1_enc_2, cx1_enc_3, cx1_enc_4, cx1_compute_1, cx1_compute_2, cx1_dec_1, cx1_dec_2, cx1_dec_3, cx1_dec_4,
                dec_6, dec_7,
                cx2_enc_1, cx2_enc_2, cx2_enc_3, cx2_enc_4, cx2_compute_1, cx2_compute_2, cx2_dec_1, cx2_dec_2, cx2_dec_3, cx2_dec_4 
                )
    

    # utility functions
    def _create_qubit_map(self, new_qargs):
        '''
        Creates a map between old and new qargs to be used for update the position of operation.
        Note: create expanded compute space such that 0 -> (0,1,2), 1 -> (3,4,5), 2 -> (6,7,8)

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
            qarg_map[i] = 3*qargs
            qarg_map[i+1]= 3*qargs+1
            qarg_map[i+2]= 3*qargs+2
        return qarg_map



