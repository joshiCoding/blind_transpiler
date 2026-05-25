from qiskit import QuantumCircuit
from math import pi

class QPECircuit:
    def __init__(self):
        self.n_qubits = None
        self.qubits = None
        self.inp_qubits = None 
        self.out_qubit = None


    def apply_qft(self, qubits, circ=None):
        n = len(qubits)

        if circ == None:
            circ = QuantumCircuit(n)

        for i in range(n):
            # Hadamard
            circ.h(qubits[i])

            # Controlled phase rotations
            for j in range(i+1, n):
                angle = pi / (2 ** (j - i))
                # circ.cp(angle, qubits[j], qubits[i])
                circ.cx(qubits[j],qubits[i])
                circ.rz(angle, qubits[i])
                circ.cx(qubits[j],qubits[i])

        # Swap qubits (reverse order)
        for i in range(n // 2):
            circ.swap(qubits[i], qubits[n - i - 1])
        return circ


    def apply_iqft(self, qubits, circ=None):
        n = len(qubits)

        if circ == None:
            circ = QuantumCircuit(n)

        # Reverse swap (undo QFT swaps)
        for i in range(n // 2):
            circ.swap(qubits[i], qubits[n - i - 1])

        # Apply inverse rotations
        for i in reversed(range(n)):
            for j in reversed(range(i + 1, n)):
                angle = -pi / (2 ** (j - i))
                circ.cx(qubits[j],qubits[i])
                circ.rz(angle, qubits[i])
                circ.cx(qubits[j],qubits[i])

            circ.h(qubits[i])

        return circ

    def apply_qpe(self, phi, n_qubits):
        """
        Quantum Phase Estimation
        
        Args:
            phi (float): phase (0 <= phi < 1)
            n_count (int): number of counting qubits
        
        Returns:
            QuantumCircuit
        """
        
        qc = QuantumCircuit(n_qubits + 1, n_qubits)
        
        # Step 1: Initialize eigenstate |1>
        qc.x(n_qubits)
        
        # Step 2: Hadamard on counting qubits
        qc.h(range(n_qubits))
        
        # Step 3: Controlled-U^(2^k)
        for qubit in range(n_qubits):
            repetitions = 2**qubit
            for _ in range(repetitions):
                angle = 2 * pi * phi
                # qc.cp(angle, qubit, n_count)
                qc.cx(qubit,n_qubits)
                qc.rz(angle, qubit)
                qc.cx(qubit,n_qubits)

        
        # Step 4: Apply inverse QFT
        qc.compose(self.apply_iqft(list(range(n_qubits))), range(n_qubits), inplace=True)
        
        # Step 5: Measure
        qc.measure(range(n_qubits), range(n_qubits))
        
        return qc

    def measure(self, circ, qubits=None):
        if qubits == None:
            circ.measure_all()
        else:
            from qiskit import ClassicalRegister
            cr = ClassicalRegister(len(qubits))
            circ.add_register(cr)
            measure_list = list(range(len(qubits)))

            # Now you can measure
            circ.measure(qubits, measure_list)

        return circ



