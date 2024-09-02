from qiskit import Aer

noise = Aer.noise

# Function to create a depolarizing error model
def depolarizing_error_model(error_rate, num_qubits):
    error = noise.depolarizing_error(error_rate, 1) # Depolarizing error for 1-qubit gates
    noise_model = noise.NoiseModel()
    for qubit in range(num_qubits):
        # Add depolarizing error to CX and H gates for each qubit
        noise_model.add_quantum_error(error, 'cx', [qubit])
        noise_model.add_quantum_error(error, 'h', [qubit])
    return noise_model

# Function to create an amplitude damping error model
def amplitude_damping_error_model(error_rate, num_qubits):
    error = noise.amplitude_damping_error(error_rate) # Amplitude damping error
    noise_model = noise.NoiseModel()
    for qubit in range(num_qubits):
        # Add amplitude damping error to CX and H gates for each qubit
        noise_model.add_quantum_error(error, 'cx', [qubit])
        noise_model.add_quantum_error(error, 'h', [qubit])
    return noise_model

# Function to create a biased noise model with different X and Z error rates
def biased_noise_model(p_x, p_z, num_qubits):
    error = noise.pauli_error([('X', p_x), ('Z', p_z), ('I', 1 - p_x - p_z)]) # Pauli error with bias
    noise_model = noise.NoiseModel()
    for qubit in range(num_qubits):
        # Add biased noise to CX and H gates for each qubit
        noise_model.add_quantum_error(error, 'cx', [qubit])
        noise_model.add_quantum_error(error, 'h', [qubit])
    return noise_model
