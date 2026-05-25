from tqdm import tqdm
from qiskit import QuantumCircuit 
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '')))

from blind_transpiler import BQC

from applications import GroverCircuit, DJCircuit, BVCircuit, QFTCircuit, QPECircuit

def create_blind_circuit( qc, format='qhe', key_style='rand_fix'):
    # circuit needs to be transpiled in server and client basis for these to work properly
    bqc = BQC() # create a new object of the circuit everytime

    keys = bqc.generate_random_key(format=format, key_size=None, circ=qc, key_style=key_style) # give one of the two arguments

    bqc_instructions  = bqc.generate_bqc(circ=qc,
                        format=format,
                        keys = keys,
                        )


    blind_circ = bqc_instructions.to_circuit(const_type='complete', show_barrier=False)

    return blind_circ        



class BaseTestCases:
    '''
    Test cases type:
        - basic single gate test cases
        - combination of gates such that output is 1
    
    New test cases:
        - different powers of rz gates
        - test cases with gates not in default gate space = ['rz','h','z','x','cx','t', 'cz', 's', 'ccx', 'swap', 'measure']
        - implement application of the bqc
            - grover
            - dj algo
            - variational algorithm
            - possibily from the PRA, or Transaction Journals


    IMPORTANT:
        test case also include randomness in key
        add U_swap gate for 3q, 4q, 5q etc.
        add multi-control multi-target qubit gates test for 4q, 5q, 6q.
    '''


    # basic gates test
    def h_circuit(self):
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.measure_all()
        return qc 

    def x_circuit(self):
        qc = QuantumCircuit(1)
        qc.x(0)
        qc.measure_all()
        return qc 
    
    def z_circuit(self):
        qc = QuantumCircuit(1)
        qc.z(0)
        qc.measure_all()
        return qc 

    def s_circuit(self):
        qc = QuantumCircuit(1)
        qc.s(0)
        qc.measure_all()
        return qc 

    def sdg_circuit(self):
        qc = QuantumCircuit(1)
        qc.sdg(0)
        qc.measure_all()
        return qc 

    def t_circuit(self):
        qc = QuantumCircuit(1)
        qc.t(0)
        qc.measure_all()
        return qc 

    def tdg_circuit(self):
        qc = QuantumCircuit(1)
        qc.tdg(0)
        qc.measure_all()
        return qc 

    def cx_circuit(self):
        qc = QuantumCircuit(2)
        qc.cx(0,1)
        qc.measure_all()
        return qc 
    
    def cz_circuit(self):
        qc = QuantumCircuit(2)
        qc.cz(0,1)
        qc.measure_all()
        return qc 
    
    def ccx_circuit(self):
        qc = QuantumCircuit(3)
        qc.ccx(0,1,2)
        qc.measure_all()
        return qc 

    # test cases that given fixed answer = |1>
    def h_unit_circuit(self):
        qc = QuantumCircuit(1)
        qc.x(0)
        qc.h(0)
        qc.h(0)
        qc.measure_all()
        return qc 

    def x_unit_circuit(self):
        qc = QuantumCircuit(1)
        qc.x(0)
        qc.x(0)
        qc.x(0)
        qc.measure_all()
        return qc 
    
    def z_unit_circuit(self):
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.z(0)
        qc.h(0)
        qc.measure_all()
        return qc 

    def s_unit_circuit(self):
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.s(0)
        qc.s(0)
        qc.h(0)
        qc.measure_all()
        return qc 

    def s_unit_circuit(self):
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.s(0)
        qc.s(0)
        qc.h(0)
        qc.measure_all()
        return qc 

    def sdg_unit_circuit(self):
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.sdg(0)
        qc.sdg(0)
        qc.h(0)
        qc.measure_all()
        return qc 

    def t_unit_circuit(self):
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.t(0)
        qc.t(0)
        qc.t(0)
        qc.t(0)
        qc.h(0)
        qc.measure_all()
        return qc 

    def tdg_unit_circuit(self):
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.tdg(0)
        qc.tdg(0)
        qc.tdg(0)
        qc.tdg(0)
        qc.h(0)
        qc.measure_all()
        return qc 
   

    def cx_unit_circuit(self):
        qc = QuantumCircuit(2)
        qc.x(0)
        qc.cx(0,1)
        qc.measure_all()
        return qc 
    
    def cz_unit_circuit(self):
        qc = QuantumCircuit(2)
        qc.x(0)
        qc.h(1)
        qc.cz(0,1)
        qc.h(1)
        qc.measure_all()
        return qc 
    
    def ccx_unit_circuit(self):
        qc = QuantumCircuit(3)
        qc.x([0,1])
        qc.ccx(0,1,2)
        qc.measure_all()
        return qc 
    
    def h0_cx_unit_circuit(self):
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0,1)
        qc.h(0)
        qc.measure_all()
        return qc 

    def h1_cx_unit_circuit(self):
        qc = QuantumCircuit(2)
        qc.h(1)
        qc.cx(0,1)
        qc.h(1)
        qc.measure_all()
        return qc 

    def h0_cz_unit_circuit(self):
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cz(0,1)
        qc.h(0)
        qc.measure_all()
        return qc 

    def h1_cx_unit_circuit(self):
        qc = QuantumCircuit(2)
        qc.h(1)
        qc.cx(0,1)
        qc.h(1)
        qc.measure_all()
        return qc 


    def h0_ccx_unit_circuit(self):
        qc = QuantumCircuit(3)
        qc.h(0)
        qc.ccx(0,1,2)
        qc.h(0)
        qc.measure_all()
        return qc 

    def h1_ccx_unit_circuit(self):
        qc = QuantumCircuit(3)
        qc.h(1)
        qc.ccx(0,1,2)
        qc.h(1)
        qc.measure_all()
        return qc 

    def h2_ccx_unit_circuit(self):
        qc = QuantumCircuit(3)
        qc.h(2)
        qc.ccx(0,1,2)
        qc.h(2)
        qc.measure_all()
        return qc 

    # testing applications
    def grover_circuit(self):
        return GroverCircuit().create_grover_circuit(n_qubits=2,target='11')

    def grover_circuit_3(self):
        circ = GroverCircuit().create_grover_circuit(n_qubits=3,target='111')
        print(circ.decompose(reps=2).draw())
        return circ

    def dj_circuit(self):
        return DJCircuit().create_dj_circuit(n_qubits=3, target='constant')

    def bv_circuit(self):
        return BVCircuit().create_bv_circuit(n_qubits=4, secret='1011')



    # test taking longer in ssdqc program

    # def rz_circuit(self):
    #     qc = QuantumCircuit(1)
    #     qc.rz(2.7654321,0)
    #     qc.measure_all()
    #     return qc 
    
    # def rz_high_circuit(self):
    #     qc = QuantumCircuit(1)
    #     qc.rz(5.3453,0)
    #     qc.measure_all()
    #     return qc

    # def rz_unit_circuit(self):
    #     qc = QuantumCircuit(1)
    #     qc.h(0)
    #     qc.rz(2.7654321,0)
    #     qc.rz(0.37616055359, 0)
    #     qc.h(0)
    #     qc.measure_all()
    #     return qc 
    

    # def rx_unit_circuit(self):
    #     from math import pi
    #     qc = QuantumCircuit(1)
    #     qc.rx(2.7654321,0)
    #     qc.rx(0.37616055359, 0)
    #     # qc.rx(pi/2,0)
    #     qc.measure_all()
    #     # print('circuit')
    #     # print(f'{qc}')
    #     return qc 


    # def qft_circuit(self):
    #     n_qubits = 2
    #     qubits = list(range(n_qubits))
    #     qft_circ = QFTCircuit().apply_qft(qubits=qubits)
    #     qft_circ = QFTCircuit().measure(qubits=qubits,circ=qft_circ)
    #     return qft_circ

    # def iqft_circuit(self):
    #     n_qubits = 2
    #     qubits = list(range(n_qubits))
    #     iqft_circ = QFTCircuit().apply_iqft(qubits=qubits)
    #     iqft_circ = QFTCircuit().measure( qubits=qubits, circ=iqft_circ)
    #     return iqft_circ

    # def qft_iqft_circuit(self):
    #     n_qubits = 2
    #     qubits = list(range(n_qubits))
    #     qft_circ = QFTCircuit().apply_qft(qubits=qubits)
    #     iqft_circ = QFTCircuit().apply_iqft(circ=qft_circ, qubits=qubits)
    #     circ = QFTCircuit().measure(iqft_circ, qubits=qubits)
    #     return circ

    # def qpe_circuit(self):
    #     n_qubits = 4
    #     from math import pi
    #     qubits = list(range(n_qubits))
    #     qpe_circ = QPECircuit().apply_qpe(phi = pi/8,n_qubits=n_qubits)
    #     return qpe_circ


'''
- exportable instance of all test cases in form of list
- Collect all circuit methods dynamically
- and create circuit using the create_blind_circuit function
- and return the output as list of tuples (name, circuit, blind_circ)
'''
def create_all_test_cases(test_case_instance):
    format = ['qhe', 'fdqc','ssdqc', 'ubqc']
    possible_key_styles = ['all_0', 'all_1', 'rand_fix', 'rand']

    test_cases = []

    for key_style in possible_key_styles:
        for name in tqdm(dir(test_case_instance)):
            func = getattr(test_case_instance, name)
            if callable(func) and not name.startswith('__'):
                for fmt in format:
                    test_cases.append((f'{name}_{fmt}_{key_style}', func(), create_blind_circuit(func(), format=fmt, key_style=key_style) ))
    
    return test_cases


test_cases = create_all_test_cases(BaseTestCases())


