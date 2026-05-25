from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
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
def blind_transpiler(circ, blind_format='hdqc', const_type='complete', key_style ='rand', keys=None):
    bqc = BQC()
    if keys == None: keys =  bqc.generate_random_key(format=blind_format,  circ=circ, key_style=key_style)
    bqc_instructions  = bqc.generate_bqc(circ=circ, format =blind_format, keys=keys)
    blind_circ = bqc_instructions.to_circuit(const_type=const_type, show_barrier=True)
    return blind_circ , bqc_instructions 

# function to run blind circuit over all keys - (too long will not work)
def run_over_all_keys(circ, blind_format, const_type):
    bqc = BQC()
    estimated_key_size = bqc.estimate_keysize(format=blind_format, circ=circ)
    possible_key_space =  [[int(bit) for bit in format(i, f'0{estimated_key_size}b')] for i in range(2**estimated_key_size)]
    print(f' key size={estimated_key_size}')
    # print(*possible_key_space, sep="\n")
    n_qubits = circ.num_qubits
    output = {output_key: 0 for output_key in [format(i, f'0{n_qubits}b') for i in range(2**n_qubits)]}
    
    for keys in tqdm(possible_key_space):
        blind_circ, _ = blind_transpiler(circ=circ,blind_format=blind_format, const_type=const_type, keys=keys)
        results = run_circuit(blind_circ).get_counts()
        for k in results.keys():
            output[k] = results[k]
    
    plot_output(output, f'{blind_format}_{const_type}')

# function to run blind circuit over all keys - (too long will not work)
def run_over_random_samples(circ, blind_format, const_type, n_samples, n_trial): # n_trial - just to track the trial file name
    bqc = BQC()
    estimated_key_size = bqc.estimate_keysize(format=blind_format, circ=circ)
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


    print(plot_histogram(output_normalized))
    plt.title(f'{title}')        
    plt.xlabel("State")       
    plt.ylabel("Probability")   
    plt.savefig(f'{title}.png')    
    plt.show()

