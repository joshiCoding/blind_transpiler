from qiskit import QuantumCircuit
from ..essentials.bop import  BOP
from ..essentials.bqc_instruction import BQCInstruction

from .qhe import QHE
from .fdqc import FDQC
from .ssdqc import SSDQC
from .ubqc import UBQC

from .base import BaseController

from ..global_value_store import GlobalVariablesAndFunctions

class BQC(BaseController):

    def __init__(self):
        BaseController.__init__(self)
        self.keys = None
        self.key_size = None

    def generate_bqc(self, circ, format='qhe', basis_gates= None, keys=None ):
        '''
        Controller function to translate a circuit to one to the four available formats:

            * qhe (Quantum Homomorphic Encryption)
            * fdqc (UBQC using ordered set of universal gates)
            * ssdqc (UBQC using fixed rotation gates)
            * ubqc (UBQC using recursive rotation gates)
        
        Args:
            circ (QuantumCircuit):
                object of quantum circuit
            format (str):
                accepted formats are the four available format: 'qhe', 'fdqc', 'ssdqc', and 'ubqc'
            basis_gates (list[str]):
                righnow not supported, might be helpfull later
            keys (str):
                string of binary random integers, need to generated using .generate_random() function of this class or need to generated size of random keys using .estimate_keysize() function

        Returns:
            bqc_instructions (BQCInstruction):
                list of all the instruction of BOP class

            
        Library Dependency:
            random

            
        '''


        if basis_gates is None: 
            basis_gates = self.default_basis_gates

        if keys is None: 
            keys = self.generate_random_key(format=format, circ=circ)  # define range by size of qc (done)

        key_size = self.estimate_keysize( format=format, circ=circ)  # checking if the given key size is smaller than expected
        if len(keys) < key_size:
            import warnings
            warnings.warn(f'Overriding random key. Key size {len(keys)} given was insufficient (Needed={key_size})', category=UserWarning)
            keys = self.generate_random_key(format=format, circ=circ)  # define range by size of qc (done)


        if format == 'ssdqc': # not implemented
            bqc_instructions = SSDQC().ssdqc(self.transpiled_circ, keys)
        elif format == 'fdqc':
            bqc_instructions = FDQC().fdqc(self.transpiled_circ, keys)
        elif format == 'qhe':
            bqc_instructions = QHE().qhe(self.transpiled_circ, keys)
        elif format == 'ubqc':
            bqc_instructions = UBQC().ubqc(self.transpiled_circ, keys)

        # store the key value in the class object
        self.keys = keys
        self.key_size = len(keys)
        
        # return the values
        return bqc_instructions
    
    def transpile_circuit(self, circ: QuantumCircuit, format: str ) -> QuantumCircuit:
        '''
        Transpiles the circuit into given basis set to be translated into blind form as written in translator library.
        
        Args:
            circ (QuantumCircuit):
                object of quantum circuit
            basis_gates (list[str]):
                rightnow, based on the default basis gates defined in init function of this class.

        Returns:
            transpiled_circ (QuantumCircuit):
                output of transpiled circuit.

        Library Dependency:
            qiskit.transpiler.preset_passmanager:
                generate_preset_pass_manager
                
        '''

        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
        from qiskit.transpiler import PassManager
        from qiskit.transpiler.passes import SolovayKitaev

        GVF = GlobalVariablesAndFunctions()
        self._generate_basis(format) # will store the correst values for client and server basis according to format given
        # need to run this before using the default_basis_gates variable of base class, which depends on format

        pm = generate_preset_pass_manager(
            optimization_level=GVF.optimization_level, # Note with optimization_level > 1, transpiler is sometimes not working.
            basis_gates=self.default_basis_gates + ['rz'] # as rz gate is not in fdqc and ssdqc default basis, hence giving error
            # solution is to first transpile circuit with availability of rz gate and then use solovay pass if the basis set do not have rz gate
        )

        transpiled_circ = pm.run(circ)
        if 'rz' not in self.default_basis_gates:  # if rz is not present then transpilation should be using solovay kitaev
            pm = PassManager(SolovayKitaev(recursion_degree=GVF.recursion_degree, 
                                           basis_gates=['x','z','h','s','sdg','t','tdg']
                                           )) 
            transpiled_circ = pm.run(transpiled_circ)

            transpiled_circ = pm.run(transpiled_circ)


        self.transpiled_circ = transpiled_circ
        # print(transpiled_circ)
        return transpiled_circ
    


    ########### utility functions ####################################################################################################

    def estimate_keysize(self, format, circ):
        '''
        Estimate the size of random key needed to perform classically assisted blind quantum computation. The size of key will be dependent on the format in which the circuit is needed to be blinded, and the circuit itself.

        Args:
            format (str):
                is a str having one of the four available format: 'qhe', 'fdqc', 'ssdqc', and 'ubqc'
            circ (QuantumCircuit):
                the circuit that need to be blinded.

        Returns:
            n_keys (int):
                size of the random key needed.

        Raises:
            ValueError(f'Instr: {instr.name} not in basis_set')
            
        '''

        n_keys = 0

        if self.transpiled_circ ==None:
            self.transpiled_circ = self.transpile_circuit(circ, format)


        # print(transpiled_circ.draw())
        # print(f'ubqc server basis {server_basis}')
        for data in self.transpiled_circ.data:
            instr = data.operation
            # print(f'given inst {instr.name}')
            if instr.name in self.server_basis:
                n_keys += self.key_estimate[format][instr.name]

            if instr.name not in self.default_basis_gates and instr.name != 'barrier':
                raise ValueError(f'Instr: {instr.name} not in basis_set')
            
        return n_keys
    
    
    def generate_random_key(self, key_size=None, format=None,  circ=None, key_style='rand'):
        '''
        Generate random key needed to perform classically assisted blind quantum computation. The size of key will be dependent on the format in which the circuit is needed to be blinded, and the circuit itself.
        Need to give either key_size pregenerated with 'estimate_key' function or circ and format to generate the keysize using estiamte_key and then generate key.

        Args:
            key_size (int):
                size of random key needed to blind the given circuit in given format.
            format (str):
                is a str having one of the four available format: 'qhe', 'fdqc', 'ssdqc', and 'ubqc'
            circ (QuantumCircuit):
                the circuit that need to be blinded.
            key_style
                attain four values 'rand', 'all_0', 'all_1', 'rand_fix'

        Returns:
            n_keys (int):
                size of the random key needed.

        Raises:
            ValueError('Give one of the two (key_size or (circ and format)) to generate the random key')

        Library Dependency:
            random

        Future Work:
            take random seed from user, as optional choice
            
        '''

        import random 
        if (key_size is None) & (circ is None or format is None): # Xor condition
            raise ValueError('Give one of the two (key_size or (circ and format)) to generate the random key')
        
        if key_size is None:   # if keysize is not given then use circ to estimate the key size first
            key_size = self.estimate_keysize(format=format, circ=circ)

        key = None 
        if key_style == 'rand':
            key = random.choices([0, 1], k=key_size) 
        elif key_style == 'all_0':
            key = random.choices([0], k=key_size) 
        elif key_style == 'all_1':
            key = random.choices([1], k=key_size)  
        elif key_style == 'rand_fix':
            random.seed(42)  
            key = random.choices([0,1], k=key_size)  

        return key
            



bqc = BQC()


    
