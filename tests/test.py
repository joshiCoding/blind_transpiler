import pytest
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '')))

from test_cases import test_cases


class TestBlindQuantumCircuits:

    @pytest.mark.parametrize("name_and_qc", test_cases, ids=[name for name, _ , _ in test_cases])
    def test_blind_circuit_equivalence(self, name_and_qc):
        name, circ, blind_circ = name_and_qc

        print(circ)
        print(blind_circ)

        result_orig = self.run_circuit(circ)
        result_blind = self.run_circuit(blind_circ)

        counts_orig = result_orig.get_counts()
        counts_blind = result_blind.get_counts()


        assert self.counts_are_equivalent(counts_orig, counts_blind), \
            f"Mismatch in circuit {name} results.\nOriginal: {counts_orig}\nBlind: {counts_blind}"
        

    # helper functions
    def counts_are_equivalent(self, counts1, counts2, tolerance=0.0999):
        """Check if two result count dicts are approximately equal within tolerance."""
        keys = set(counts1.keys()) | set(counts2.keys())
        total1 = sum(counts1.values())
        total2 = sum(counts2.values())

        for key in keys:
            freq1 = counts1.get(key, 0) / total1
            freq2 = counts2.get(key, 0) / total2
            if abs(freq1 - freq2) > tolerance:
                return False
        return True
    

    

    
    def run_circuit(self, qc):
        # running the blind circuit
        from qiskit_aer import Aer
        from qiskit import transpile
        from qiskit.visualization import plot_histogram
        import matplotlib.pyplot as plt

        backend = Aer.get_backend('aer_simulator')
        shots = 1000

        t_qc = transpile(qc, backend)

        results = backend.run(t_qc, shots=shots).result()

        return results
    
    



