class BQCInstruction:
    def __init__(self):
        '''
        Class object of the output, contains:

        Instruction_list (List[BOP]): store the output of the conversion in form list of BOP circuits. It is list of tuples (step, BOP)
        n_qubits (int): store the number of qubits
        n_cbits (int): stores the number of classical bits.
        
        '''

        self.instruction_list =  []
        self.n_qubits = None    # updated while the blinding the circuit
        self.n_cbits = None     # updated while the blinding the circuit

        self.n_client_gates = 0
        self.n_server_gates = 0
        self.n_secure_gates = 0 # gives the number of X,Z, Swap and Measure gate
        self.n_communication_rounds = 0
        self.bandwidth = 0 

        self.format = None


        # temp variable to test only
        self.truncated_instruction_list = None 
    
    def get_metadata(self):
        return (self.format, self.n_client_gates, self.n_server_gates, self.n_secure_gates,self.n_communication_rounds,self.bandwidth)

    def print_metadata(self):
        print(f'BQC Instruction Meta Data:')
        print(f'\tBlinding Format = {self.format} \n\tClient gates used = {self.n_client_gates} \n\tServer gates used = {self.n_server_gates} \n\tSecure gates used = {self.n_secure_gates} \n\tCommunication Rounds needed = {self.n_communication_rounds}')

    def _update_metadata(self, BOP):
        if BOP.op_type in ['client','measure']:   # client_basis can be use to update this, rightnow using indirect relationship
            self.n_client_gates += 1
        elif BOP.op_type in ['enc','dec','swap']:
            self.n_secure_gates += 1

        # server resources and communication rounds are format specifice (written in intuitive way deemed suitable for future extensions, otherwise can also be written as if BOP.op_type in ['compute','trap'])
        if self.format == 'qhe':
            if BOP.op_type == 'compute':
                self.n_server_gates += 1
                self.n_communication_rounds += 1
                self.bandwidth = 1 # will be updated only once with constant value, might keep it somewhere else to save execution time, however, this place makes more sense (but it depends on the number of gates transmitted which depends on the number type of gates in case of 'qhe' only) so her bandwidth will be = (1q_gate + 2q_gates*2 + 3q_gates*3) / n_g
        elif self.format == 'fdqc':
            if BOP.op_type  == 'compute':
                self.n_server_gates += 11 # each compute resource in fdqc contains 11 basis gates
                self.n_communication_rounds += 1 # all 11 qubits are performed at once.
                self.bandwidth = 11 # will be updated only once with constant value, might keep it somewhere else to save execution time, however, this place makes more sense
        elif self.format == 'ssdqc':
            if BOP.op_type in ['compute','trap']:
                self.n_server_gates += 1
                self.n_communication_rounds += 1
                self.bandwidth = 3 # will be updated only once with constant value, might keep it somewhere else to save execution time, however, this place makes more sense
        elif self.format == 'ubqc':
            if BOP.op_type == 'compute':
                self.n_server_gates += 1
                self.n_communication_rounds += 1
                self.bandwidth = 4 # will be updated only once with constant value, might keep it somewhere else to save execution time, however, this place makes more sense
        else:
            raise ValueError(f'Something went wrong with {self.format} controller.')
        

    def add_elements(self, elem):
        '''
        It is used to add new BOP element to the variable instruction_list. 
        This fuction can handle elem as object BOP or the list of BOP class.

        Args:
            elem (BOP/ List[BOP]): 
                elem to be added to list, can be object of class BOP or list of object of class BOP.

        '''

        if not isinstance(elem, list):
            self._update_metadata(elem)
            self.instruction_list.append(elem)
        else:
            for bop in elem:
                self._update_metadata(bop)
                self.instruction_list.append(bop)


    def __repr__(self):
        return f"{self.instruction_list}"
    
    def __iter__(self):
        return iter(self.instruction_list)
    

    def _remove_trailing_dec_per_qubit(self, bqc_instruction_list):
        new_bqc_instruction_list = []
        seen_qubits = []
        bqc_instruction_list = bqc_instruction_list[::-1]
        for bop in bqc_instruction_list:
            if bop.op_type != 'dec' and bop.gate.name != 'id':
                new_bqc_instruction_list.append(bop)
            else: 
                for q in bop.qargs:
                    if q not in seen_qubits:
                        seen_qubits.append(q)
                    else:
                        new_bqc_instruction_list.append(bop)
        new_bqc_instruction_list = new_bqc_instruction_list[::-1]
        return new_bqc_instruction_list


    def to_circuit(self, const_type='complete', show_barrier=False):
        '''
        Create the quantum circuit using list of BOP class objects based on the conditional provided to them.
        
        Args:
            bqc_instruction (list[BOP]):
                the list of BOP object that contain the gate object needed to be applied at each step to form the bqc circuit with given key, based on conditional value.
            const_type (str):
                circuit can be constructed of four different types:
                    'complete': all the client and server gates are present, circuit is complete functional blind circuit.
                    'client_only': contains only gates corresponding to the client. It is not functional blind circuit, and should only be used for resource estimation of client side and other similar tasks.
                    'server_only': contains only gates corresponding to the server. It is not functional blind circuit, and should only be used for resource estimation of server side and other similar tasks.
                    'encrypt_only': contain no decryption gate for the operations performed. Not a functional blind circuit, can be used to verify the blindness of data at server end. At the end of presentation.
            show_barrier (boolean):
                flag that controlls if the circuit will contain barrier or not.

        Returns:
            qc (QuantumCircuit)
                a quantum circuit that performs same operation as original circuit, with exception of global phase shift, but is completly blind.

        Raises:
            ValueError(f'const_type {const_type} not available. Kindly choose from "complete", "client_only", "server_only", "encrypt_only".')

        Library Dependency:
            qiskit:
                QuantumCircuit
        
            
        '''
        from qiskit import QuantumCircuit
        # print(f'const_type {const_type}')
        bqc_instruction_list = self.instruction_list

        if not isinstance(const_type, str):   # type checking the input of const_type
            raise ValueError(f'const_type {const_type} not available. Kindly choose from "complete", "client_only", "server_only", "encrypt_only", and "exclude_last_dec".')
        elif const_type == 'complete':
            check = ['client','enc','dec','swap','trap','measure','barrier','compute' ]
        elif const_type == 'client_only':
            check = ['client','enc','dec','swap','measure','barrier']
        elif const_type == 'server_only':
            check = ['compute', 'trap', 'measure']
        elif const_type == 'encrypt_only':
            check = ['client','enc','trap','measure','barrier','compute' ] # note swap gates are also exclude, because they also work as decryption gates, whose value depend on encryption keys.
        elif const_type == 'exclude_last_dec':
            check = ['client','enc','dec','swap','trap','measure','barrier','compute' ]
            bqc_instruction_list = self._remove_trailing_dec_per_qubit(bqc_instruction_list)
            self.truncated_instruction_list = bqc_instruction_list
        else:
            raise ValueError(f'const_type {const_type} not available. Kindly choose from "complete", "client_only", "server_only", "encrypt_only" and "exclude_last_dec".')
        
        if not isinstance(show_barrier, bool):
            import warnings
            warnings.warn(f"show_barrier {show_barrier} is note bool type. Overriding by False", UserWarning)
            show_barrier = False


        qc = QuantumCircuit(self.n_qubits, self.n_cbits) 
        for instr in bqc_instruction_list:
            if show_barrier and instr.op_type == 'compute': qc.barrier()    # add barrier to show server operation
            if instr.op_type in check:
                if instr.conditional == 1:
                    qc.append(instr.gate, instr.qargs, instr.cargs)
            if show_barrier and instr.op_type == 'compute': qc.barrier()    # add barrier to show server operation
        return qc
