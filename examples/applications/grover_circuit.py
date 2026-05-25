from qiskit import QuantumCircuit
from qiskit.circuit.library import MCMTGate, ZGate
from math import pi

class GroverCircuit:
    def __init__(self):
        self.qubits = None
        self.CNZGate = None

    def create_oracle(self, target):
        n = len(target)

        oracle = QuantumCircuit(n, name=f'oracle({target})')

        for i, q in enumerate(target): 
            # print(f'i: {i},q: {q}')
            if q == '0': oracle.x(i)
        oracle.append(self.CNZGate, self.qubits)
        for i, q in enumerate(target): 
            if q == '0': oracle.x(i)

        return oracle.to_instruction()
    
    def create_grover_circuit(self, n_qubits: int, target: str) -> QuantumCircuit:
        from math import floor, sqrt, pi
        
        self.qubits = list(range(n_qubits))
        
        self.CNZGate = MCMTGate(ZGate(), n_qubits-1, 1)

        itr = floor(sqrt(2**n_qubits) * pi /4) # number of iteration

        oracle = self.create_oracle(target)
        grover_circuit = QuantumCircuit(n_qubits)

        #1.superposition
        grover_circuit.h(self.qubits)

        for _ in range(itr):
            grover_circuit.append(oracle, self.qubits)

            grover_circuit.h(self.qubits)

            # diffusion
            grover_circuit.x(self.qubits)
            grover_circuit.append(self.CNZGate, self.qubits)
            grover_circuit.x(self.qubits)

            grover_circuit.h(self.qubits)
        
        grover_circuit.measure_all()
        return grover_circuit


