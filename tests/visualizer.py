from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from blind_transpiler import BQC
import matplotlib.pyplot as plt 
from math import pi
from tqdm import tqdm
import random
import warnings

# function to run circuit
def run_circuit(circ):
    backend = AerSimulator()
    shots = 1000
    t_circ = transpile(circ, backend)
    results = backend.run(t_circ, shots=shots).result()
    return results

# function to convert circuit to blind
def blind_transpiler(circ, blind_format='qhe', const_type='complete', key_style ='rand', keys=None):
    bqc = BQC()
    if keys == None: keys =  bqc.generate_random_key(format=blind_format,  circ=circ, key_style=key_style)
    bqc_instructions  = bqc.generate_bqc(circ=circ, format =blind_format, keys=keys)
    blind_circ = bqc_instructions.to_circuit(const_type=const_type, show_barrier=True)
    return blind_circ , bqc_instructions 


# function to run blind circuit over all keys - (too long will not work)
def run_over_random_samples(circ, blind_format, const_type, n_samples, n_trial): # n_trial - just to track the trial file name
    bqc_trial = BQC()
    estimated_key_size = bqc_trial.estimate_keysize(format=blind_format, circ=qc)
    if n_samples > 2**estimated_key_size:
        warnings.warn(f' Overriding sample size as sample size {n_samples} is bigger than possible key space {2**estimated_key_size}.', UserWarning)
        n_samples = 2**estimated_key_size
    random_sample_key_space =  generate_binary_samples(n_samples,estimated_key_size)
    n_clbits = circ.num_clbits
    output = {output_key: 0 for output_key in [format(i, f'0{n_clbits}b') for i in range(2**n_clbits)]}
    
    for keys in tqdm(random_sample_key_space):
        blind_circ, _ = blind_transpiler(circ=circ,blind_format=blind_format, const_type=const_type, keys=keys)
        results = run_circuit(blind_circ).get_counts()
        for k in results.keys():
            output[k] = results[k]
    
    plot_output(output, f'results/{blind_format}_{const_type}_{n_trial}')

def generate_binary_samples(n, key_size):
    return [[random.randint(0, 1) for _ in range(key_size)] for _ in range(n)]


# function to draw result
def plot_output(output , title):
    # output = run_circuit(circ).get_counts()
    # clean the results
    print(f'output in plot {output}')
    n_qubits = len(next(iter(output.keys())))
    possible_output_space = [format(i, f'0{n_qubits}b') for i in range(2**n_qubits)]
    output_normalized = {output_key: 0 for output_key in possible_output_space}

    for k in output_normalized.keys():
        if k in output.keys():
            output_normalized[k] += output[k]
    # calculate normalization factor
    normalization_factor = 0
    for v in output_normalized.values():
        normalization_factor += v
    # normalize the output
    for k,v in output_normalized.items():
        output_normalized[k] = v/normalization_factor

    
    print(f'output in plot {output_normalized}')

    # Extract keys and values
    labels = list(output_normalized.keys())
    values = list(output_normalized.values())

    # Create bar chart (histogram-style for categorical data)
    plt.figure()
    plt.bar(labels, values)

    # Labels and title
    plt.title(f'{title}')        
    plt.xlabel("State")       
    plt.ylabel("Probability")   
  
    # Show plot
    plt.savefig(f'{title}.png')    
    plt.show()




# create program

# define variables
n_samples = 1000
const_type = 'complete'
key_style = 'rand'


n_trial = 1
n_qubits = 3
blind_format = 'qhe'

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0,1)
qc.cx(1,2)
qc.measure_all()

print(qc.draw(output='mpl', filename=f'results/original_circuit_{n_trial}.png'))

# create blind circuit
blind_circuit, bqc_instruction = blind_transpiler(qc, blind_format, const_type='complete', key_style='rand_fix')

bqc_instruction.print_meta_data()

print(blind_circuit.draw(output='mpl', filename=f'results/blind_circuit_{n_trial}.png'))

# create the random sample and perform NIST test on it.
plot_output(run_circuit(qc).get_counts(),f'results/original_output_{n_trial}')
run_over_random_samples(circ=qc, blind_format=blind_format, const_type='exclude_last_dec', n_samples=n_samples, n_trial=n_trial)
run_over_random_samples(circ=qc, blind_format=blind_format, const_type='encrypt_only', n_samples=n_samples, n_trial=n_trial)
run_over_random_samples(circ=qc, blind_format=blind_format, const_type='complete', n_samples=n_samples, n_trial=n_trial)
