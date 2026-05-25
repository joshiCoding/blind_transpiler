from qiskit import QuantumCircuit

class BVCircuit:
    def __init__(self):
        self.n_qubits = None
        self.qubits = None
        self.inp_qubits = None 
        self.out_qubit = None

    def create_oracle(self, secret):
        n = len(secret)
        oracle = QuantumCircuit(n + 1)
        
        for i, bit in enumerate(secret):
            if bit == '1':
                oracle.cx(i, n)  # apply CNOT if secret_i = 1
        
        return oracle.to_instruction()

    def create_bv_circuit(self, n_qubits: int, secret: str) -> QuantumCircuit:
        from math import floor, sqrt, pi

        n_inp = n_qubits 
        n_out = 1
        
        self.n_qubits = n_inp + n_out
        self.qubits = list(range(n_inp+n_out))
        self.inp_qubits = list(range(n_inp))
        self.out_qubit = [n_inp]
        
        oracle = self.create_oracle(secret)
        bv_circuit = QuantumCircuit(self.n_qubits,n_inp)

        # 0. prepare ancilla (last qubit of circuit)
        bv_circuit.x(self.n_qubits-1)

        #1.superposition
        bv_circuit.h(self.qubits)

        #3. apply oracle
        bv_circuit.append(oracle,self.qubits)

        #4. diffuse the superposition
        bv_circuit.h(self.inp_qubits)

        #5. measure input qubits
        bv_circuit.measure(self.inp_qubits,self.inp_qubits)


        return bv_circuit


