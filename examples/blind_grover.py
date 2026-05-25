from helper_functions import run_circuit, blind_transpiler, run_over_random_samples, plot_output


# create program

# define variables
n_qubits = 3
n_samples = 1000
blind_format = 'qhe'
const_type = 'complete'
key_style = 'rand'



n_trial = 5
from applications import GroverCircuit
qc = GroverCircuit().create_grover_circuit(n_qubits=n_qubits,target='101')
print(qc.draw(output='mpl', filename=f'results/original_circuit_{n_trial}.png'))




# create blind circuit
blind_circuit, bqc_instructions = blind_transpiler(qc, blind_format, const_type='complete', key_style='rand_fix')
bqc_instructions.print_metadata()
print(blind_circuit.draw(output='mpl', filename=f'results/blind_circuit_{n_trial}.png'))

# create the random sample and perform NIST test on it.
plot_output(run_circuit(qc).get_counts(),f'results/original_output_{n_trial}')
run_over_random_samples(circ=qc, blind_format=blind_format, const_type='encrypt_only', n_samples=n_samples, n_trial=n_trial)
run_over_random_samples(circ=qc, blind_format=blind_format, const_type='complete', n_samples=n_samples, n_trial=n_trial)
