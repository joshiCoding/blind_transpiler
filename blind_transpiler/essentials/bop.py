from typing import List, Dict, Tuple, Set, Union, Optional, Callable, Any, Literal
from qiskit.circuit import Instruction
from qiskit import QuantumCircuit


class BOP:

    def __init__(self, op_type: str , qargs: Tuple, cargs: Tuple, gate: Instruction, conditional: Literal[0, 1] = 1, gate_seq:int = None) -> None:
        '''
        BOP (Blind Operator)

        Intializer of the blind operator class

        Args:
            op_type (str):
                can be 'client', 'enc', 'dec', 'compute', 'swap' (for fdqc), trap (for ssdqc), measure (for measurement)
            qargs (tuple):
                the relative position of qubit on which gate has to be applies
            cargs (tuple): 
                the relative position of cbits, used for measurement. 
            gate (BOP):
                object of Instruction class - keeps the object of gate to applies on qargs and cargs
            conditional ({0,1}):
                store the info, if gates needs to be applies or not, decided based on the conditional argument, it is precaluculated as the function is called. 
                It is chosen to store this gate instead of removing, to preserve the complete circuit information.
            gate_seq (int):
                used to store the information of which gate from original circuit, this translation is coming from.

                
        Returns:
            None

        Raise: 
            None

            
        Library Dependency:
            qiskit.circuit.library:
                IGate

        Future Works:
            library does not support conditional circuits like c_if

        '''
        from qiskit.circuit.library import IGate

        # add typechecking to verify the initialization 
        self.op_type = op_type       # op_type can be 'client', 'enc', 'dec', 'compute', 'swap' (for fdqc), trap (for ssdqc), measure (for measurement), barrier (for visual add)
        self.qargs = qargs     # tuple 
        self.cargs = cargs
        self.gate = gate if conditional == 1 else IGate()     # no need to conditional now, it will be just for record keeping.
        self.conditional = int(conditional)  # the default value of conditional is 1 because conditional is not given for compute gate which need to be done 

        self.gate_seq = gate_seq # keeps track of check gate the circuit of enc, compute, dec belong in unblind circuit
        self.id = None # keep trac of the number of gates in the circuit, it is update in the BQCInstruction class, when it is added to the bqc_instruction list, it will be helpful when finding the last decryption gate in the circuit.

    def __repr__(self):
        return f"BOP(gate='{self.gate.name}',op_type={self.op_type},qargs={self.qargs},cargs={self.cargs},conditional={self.conditional},seq={self.gate_seq})"


    def conditional_and(self, x):
        '''
        Modifies the conditional of the self class object with Binary ANDing it with incoming x.

        Args:
            x ({0,1}):
                binary conditional, can be 0 or 1.

        Returns:
            BOP
                x & conditional of the current object of class, use to apply gate like condtional cx,cz gate in ccx decryption and other similar situations.

        Raise: 
            None
   
        Library Dependency:
            None
        '''
        self.conditional = x & self.conditional
        return self
