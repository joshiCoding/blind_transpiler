from qiskit import QuantumCircuit

class DJCircuit:
    def __init__(self):
        self.n_qubits = None
        self.qubits = None
        self.inp_qubits = None 
        self.out_qubit = None


    def create_balanced_oracle(self):
        oracle = QuantumCircuit(self.n_qubits)
        
        for i in range(self.n_qubits-1):
            oracle.cx(i, self.n_qubits-1)  # XOR all inputs into ancilla
        
        return oracle.to_instruction()

    def create_constant_oracle(self, output=0):
        oracle = QuantumCircuit(self.n_qubits)

        if output == 1:
            oracle.x(self.n_qubits-1) # flip output if 1 is needed in output, not related to input
        
        return oracle.to_instruction()

    def create_dj_circuit(self, n_qubits: int, target: str) -> QuantumCircuit:
        from math import floor, sqrt, pi

        n_inp = n_qubits 
        n_out = 1
        
        self.n_qubits = n_inp + n_out
        self.qubits = list(range(n_inp+n_out))
        self.inp_qubits = list(range(n_inp))
        self.out_qubit = [n_inp]
        
        if target == 'balanced':
            oracle = self.create_balanced_oracle()
        elif target == 'constant':
            oracle = self.create_constant_oracle(1)
        dj_circuit = QuantumCircuit(self.n_qubits,n_inp)

        # 0. prepare ancilla (last qubit of circuit)
        dj_circuit.x(self.n_qubits-1)

        #1.superposition
        dj_circuit.h(self.qubits)

        #3. apply oracle
        dj_circuit.append(oracle,self.qubits)

        #4. diffuse the superposition
        dj_circuit.h(self.inp_qubits)

        #5. measure input qubits
        dj_circuit.measure(self.inp_qubits,self.inp_qubits)


        return dj_circuit


