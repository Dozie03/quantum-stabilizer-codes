from qiskit import QuantumCircuit, Aer, transpile, execute
from error_models import depolarizing_error_model, amplitude_damping_error_model, biased_noise_model

def create_surface_code_circuit(code_distance):
    num_qubits = code_distance ** 2
    qc = QuantumCircuit(num_qubits, num_qubits)
    for i in range(num_qubits):
        qc.h(i)
    for i in range(code_distance - 1):
        qc.cx(i, i + 1)
    return qc

def simulate_with_noise(qc, noise_model):
    backend = Aer.get_backend('qasm_simulator')
    qc_transpiled = transpile(qc, backend)
    job = execute(qc_transpiled, backend, shots=1024, noise_model=noise_model)
    result = job.result()
    return result
