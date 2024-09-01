from qiskit.providers.aer import noise

def depolarizing_error_model(error_rate, num_qubits):
    error = noise.depolarizing_error(error_rate, 1)
    noise_model = noise.NoiseModel()
    for qubit in range(num_qubits):
        noise_model.add_quantum_error(error, 'cx', [qubit])
        noise_model.add_quantum_error(error, 'h', [qubit])
    return noise_model

def amplitude_damping_error_model(error_rate, num_qubits):
    error = noise.amplitude_damping_error(error_rate)
    noise_model = noise.NoiseModel()
    for qubit in range(num_qubits):
        noise_model.add_quantum_error(error, 'cx', [qubit])
        noise_model.add_quantum_error(error, 'h', [qubit])
    return noise_model

def biased_noise_model(p_x, p_z, num_qubits):
    error = noise.pauli_error([('X', p_x), ('Z', p_z), ('I', 1 - p_x - p_z)])
    noise_model = noise.NoiseModel()
    for qubit in range(num_qubits):
        noise_model.add_quantum_error(error, 'cx', [qubit])
        noise_model.add_quantum_error(error, 'h', [qubit])
    return noise_model
