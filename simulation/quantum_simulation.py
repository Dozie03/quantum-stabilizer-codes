from qiskit import QuantumCircuit, Aer, transpile, execute
from error_models import depolarizing_error_model, amplitude_damping_error_model, biased_noise_model

# Function to create a basic surface code quantum circuit
def create_surface_code_circuit(code_distance):
    num_qubits = code_distance ** 2
    qc = QuantumCircuit(num_qubits, num_qubits)
    
    # Apply Hadamard gates to all qubits
    for i in range(num_qubits):
        qc.h(i)
    
    # Apply CNOT gates between adjacent qubits
    for i in range(code_distance - 1):
        qc.cx(i, i + 1)
    
    return qc

# Function to simulate a quantum circuit with a given noise model
def simulate_with_noise(qc, noise_model):
    backend = Aer.get_backend('qasm_simulator')  # Use Qiskit's qasm simulator backend
    qc_transpiled = transpile(qc, backend)  # Transpile the circuit for the backend
    job = execute(qc_transpiled, backend, shots=1024, noise_model=noise_model)  # Execute the circuit with noise
    result = job.result()  # Get the simulation result
    return result
