from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from math import pi
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
from blind_transpiler import BQC


def run_circuit(qc):
    backend = Aer.get_backend('aer_simulator')
    shots = 1000
    t_qc = transpile(qc, backend)
    results = backend.run(t_qc, shots=shots).result()
    return results

# trial
n_qubits = 3
qc = QuantumCircuit(n_qubits)
qc.h(0)
qc.cx(0,1)
qc.cx(1,2)
qc.measure_all()

# simulate original circuit
print(qc.draw())
results = run_circuit(qc)
print(plot_histogram(results.get_counts()))
plt.show()

# transpile to blind circuit
bqc = BQC()
keys = bqc.generate_random_key(format='qhe',  circ=qc, key_style='rand')
bqc_instructions = bqc.generate_bqc(circ=qc, format ='qhe', keys=keys)

# simulate encrypted circuit
encrypt_blind_circ = bqc_instructions.to_circuit(const_type='encrypt_only', show_barrier=True)
print(plot_histogram(run_circuit(encrypt_blind_circ).get_counts()))
plt.show()

# simulate correct circuit
complete_blind_circ = bqc_instructions.to_circuit(const_type='complete', show_barrier=True)
print(plot_histogram(run_circuit(complete_blind_circ).get_counts()))
plt.show()
