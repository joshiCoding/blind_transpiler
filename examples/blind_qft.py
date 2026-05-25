from helper_functions import run_circuit, blind_transpiler, run_over_random_samples, plot_output


# create program

# define variables
n_qubits = 3
n_samples = 1000
blind_format = 'qhe'
const_type = 'complete'
key_style = 'rand'


n_trial = 3
from applications import QFTCircuit
qubits = list(range(n_qubits))
qft_circ = QFTCircuit().apply_qft(qubits=qubits)
iqft_circ = QFTCircuit().apply_iqft(circ=qft_circ, qubits=qubits)
circ = QFTCircuit().measure(iqft_circ, qubits=qubits)
qc = circ
print(qc.draw(output='mpl', filename=f'results/original_circuit_{n_trial}.png'))



# create blind circuit
blind_circuit, bqc_instructions = blind_transpiler(qc, blind_format, const_type='complete', key_style='rand_fix')
bqc_instructions.print_metadata()
print(blind_circuit.draw(output='mpl', filename=f'results/blind_circuit_{n_trial}.png'))

# create the random sample and perform NIST test on it.
plot_output(run_circuit(qc).get_counts(),f'results/original_output_{n_trial}')
run_over_random_samples(circ=qc, blind_format=blind_format, const_type='encrypt_only', n_samples=n_samples, n_trial=n_trial)
run_over_random_samples(circ=qc, blind_format=blind_format, const_type='complete', n_samples=n_samples, n_trial=n_trial)
