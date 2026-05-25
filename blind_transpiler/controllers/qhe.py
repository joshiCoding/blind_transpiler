from ..essentials.bqc_instruction import BQCInstruction
from ..essentials.bop import BOP
from ..translators.homomorphicTranslator import HomomorphicTranslation
from .base import BaseController
from ..global_value_store import GlobalVariablesAndFunctions


# class HDQC(BaseController):
class QHE(BaseController):
    def __init__(self):
        BaseController.__init__(self)

        None

    def qhe(self, trans_circ, keys):
        '''
        Convert the circuit in half-blind quantum computation circuit.
        Note: An efficient way to coding might be through converting to DAG and adding the circuit, for now do the easy one.

        Logic:
            iterate the circuit element by element
                check if element is client implementable
                    add instruction as op_type = 'client'
                if not 
                    used 'HomomorphicTranslation' class to convert get the sequence of gates and store in list with order no.
        
        Args:
            trans_circ (QuantumCircuit):
                transpiled circuit in the basis set whose translation is present in translator library.
        Returns:
            bqc_instruction (list[BOP])
                list of BOP in order which they need to be implemented.
            
            
        '''

        GVF = GlobalVariablesAndFunctions()

        constant_compute_space = GVF.qhe_compute_space

        translation_map = self._create_translation_map(HomomorphicTranslation(), format='qhe')


        bqc_instructions = BQCInstruction()   # is list of tuples (step, Op)
        bqc_instructions.n_qubits = trans_circ.num_qubits + constant_compute_space # one ancilla qubit for recursive decryption of rz
        bqc_instructions.n_cbits = trans_circ.count_ops().get('measure', 0)
        bqc_instructions.format = 'qhe'

        key_counter = 0 

        for step, data in enumerate(trans_circ.data):
            instr = data.operation
            qargs = data.qubits
            cargs = data.clbits

            qargs = tuple([trans_circ.find_bit(q)[0] + constant_compute_space for q in qargs])   # extract index of qubit from QuantumRegister element

            cargs = tuple([trans_circ.find_bit(c)[0] for c in cargs])   # extract index of qubit from ClassicalRegister element
                

            if instr.name in self.client_basis:
                gate = instr.__class__(*instr.params)

                if instr.name == 'measure':
                    secure_gate = BOP('measure', qargs, cargs, gate, gate_seq = step )
                    #### NOTE
                    # Throughing an error if you give QC(x,x) and then apply measure_all() on it.
                else:
                    secure_gate = BOP('client', qargs, cargs, gate, gate_seq = step )
                bqc_instructions.add_elements(secure_gate)


            elif instr.name in self.server_basis:
                translation_func = translation_map[instr.name]
                gate_key_size = self.qhe_key_map[instr.name]
                if instr.name == 'rz':   # as 'rz' gate take parameter theta
                    secure_gate = translation_func(instr.params[0], tuple(keys[key_counter: key_counter+gate_key_size]), qargs, gate_seq= step)
                else:
                    secure_gate = translation_func(tuple(keys[key_counter: key_counter+gate_key_size]), qargs, gate_seq= step)

                bqc_instructions.add_elements( [*secure_gate] )

                key_counter += gate_key_size
            
            elif instr.name in ['barrier']: #barrier does not effect only visual indication, update rules outside to include it in transpiled circuit
                from qiskit.circuit.library import Barrier
                secure_gate = BOP('barrier', qargs , cargs , Barrier(len(qargs)), gate_seq = step )
                continue
            else:
                raise KeyError(f'Gate {instr.name} not in any basis set.')

        return bqc_instructions
