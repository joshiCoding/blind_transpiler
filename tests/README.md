# Testing the Library
The purpose of this test suite is to the test the functionality of the library `blind_transpiler`.

## Folder Structure
## Project Structure

```text
tests/
│
├── __init__.py          
├── test.py        # controller of the tests
├── test_cases.py       # list of test cases
├── visualizer.py        # visualize the individual results
├── applications/                  # application implementation
│   └── __init__.py
│   └── bernstein_vazirani.py
│   └── deustuch_jozsa.py
│   └── grover_circuit.py
│   └── quantum_fourier_transform.py
│   └── quantum_phase_estimation.py
├── README.md                  

```

Here, note the applications folder has implementation of pure algorithm, which can be transformed to blind version, when using the test case.
The `test.py` is the controller of the testing library and calls upon the `test_case.py` to build the test cases.

## Description of Test Cases
Currently, the library has 40 independent test cases, which can be divide in three categories:
1. Cases to test the output of single implementation of gates, where output can be anything.
2. Cases to test the output of the circuit with one type of gate which gives output = 1.
3. Cases that test the application of library for correctness on:
    1. Deutsch-Jozsa Algorithm
    2. Bernstein-Vazirani Algorithm
    3. Grover's Algorithm
    4. Quantum Fourier Transform
    5. Quantum Phase Estimation

Note, the test cases involving rotation gates have been commented out for now. Because, they take too long for testing on 'ssdqc' algorithm

These test cases are use to build test for four different styles of blind transpilation:
1. 'qhe'
2. 'fdqc'
3. 'ssdqc'
4. 'ubqc'
The test the cases are built with four different testing of random keys:
1. 'all_0'
2. 'all_1'
3. 'rand_fix' (random with a fixed seed)
4. 'rand'

The test suite if capable of performing 40*4*4 = `640`


## Running the Test
To run the test, the tester has to `cd` in the folder of `tests` and then run the following command:

```bash
pytest test.py
```

If the tester want to see the verbose, then
```bash
pytest test.py -v
```

If the complete output from the library is also needed then:
```bash
pytest test.py -v -s
```

If the tester want to see the execution or where it is failing in more detail, he can also run the program as:
```bash
python test.py
```

Moreover, for visualization and debugging of the library or test code, he can probe further using `visualizer.py` file as:
```bash
python visualizer.py
```
This file collects the results in the results folder with trial number controlled by `n_trail`. This program contains runs the circuit over randomly sample keys and give the average output of the runs. 

## Creating new Test Cases
The module automatically takes new test cases as they are written in the `test_cases.py` file as a function. We can simply write a new function with appropritate name and the file will take the name of function as the name of test case and run it on four different style of blind transpilation with four different type of key intialization. This make a overall increase of `16 test cases` for each test case written in the test_case file.




## Future Extension
Future extension in test cases includes:
1. Test cases that produce random circuit with given gates with fixed output = 1.
2. Test case of variational quantum algorithms.

For improvement of the test case and logic of module:
1. allow giving the seed with 'rand_fix' setting
2. allow the setting of not running the cases where high computation is need, if user has selected quick testing option.
3. add requirements.txt file in the module
4. In visualizer.py, other methods of visualization can also be explored list, state tomograhy plot.



