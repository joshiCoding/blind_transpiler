# extended the definition of RZ, RY and CRZ, CRY to create CCRZ and CCRY class

from qiskit.circuit.library import PhaseGate, RYGate

def RZGate(theta):
    return PhaseGate(theta)

def CRZGate(theta):
    return PhaseGate(theta).control(1, annotated=True)

def CCRZGate(theta):
    return PhaseGate(theta).control(2,annotated=True)

def RYGate(theta):
    from qiskit.circuit.library import RYGate
    return RYGate(theta)

def CRYGate(theta):
    from qiskit.circuit.library import RYGate
    return RYGate(theta).control(1,annotated=True)

def CCRYGate(theta):
    from qiskit.circuit.library import RYGate
    return RYGate(theta).control(2,annotated=True)

