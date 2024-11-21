import stim
import numpy as np
from stimbposd import BPOSD

# def generate_stim_circuit(stabilizers, p, num_rounds):
#     circuit = stim.Circuit()
#     circuit.append_operation("R", range(9))

#     for round in range(num_rounds):
#         for q in range(5):
#             circuit.append_operation("X_ERROR", [q], p)

#         for i, stabilizer in enumerate(stabilizers):
#             circuit.append("H", 5 + i)
            
#             for j, pauli in enumerate(stabilizer):
#                 if pauli == 'X':
#                     circuit.append("CNOT", [5 + i, j])
#                 elif pauli == 'Z':
#                     circuit.append("CZ", [5 + i, j])
#                 elif pauli == 'Y':
#                     circuit.append("S_DAG", j)
#                     circuit.append("CNOT", [5 + i, j])
#                     circuit.append("S", j)
            
#             circuit.append_operation("M", [5+i])
#             circuit.append_operation("DETECTOR", [], [5+i])
#             circuit.append("H", 5 + i)

#         for q in range(5):
#             circuit.append_operation("Z_ERROR", [q], p)

#     circuit.append_operation("M", range(5))
#     circuit.append_operation("OBSERVABLE_INCLUDE", [stim.target_rec(-5), stim.target_rec(-4), stim.target_rec(-3), stim.target_rec(-2), stim.target_rec(-1)], 0)
#     circuit.append_operation("OBSERVABLE_INCLUDE", [stim.target_rec(-5), stim.target_rec(-4), stim.target_rec(-3), stim.target_rec(-2), stim.target_rec(-1)], 1)

#     return circuit

def generate_stim_circuit(stabilizers, p, num_rounds):
    num_data_qubits = len(stabilizers[0])
    num_stabilizers = len(stabilizers)
    total_qubits = num_data_qubits + num_stabilizers

    circuit = stim.Circuit()
    circuit.append_operation("R", range(total_qubits))

    for round in range(num_rounds):
        for q in range(num_data_qubits):
            circuit.append_operation("X_ERROR", [q], p)

        for i, stabilizer in enumerate(stabilizers):
            ancilla_qubit = num_data_qubits + i
            circuit.append("H", ancilla_qubit)
            
            for j, pauli in enumerate(stabilizer):
                if pauli == 'X':
                    circuit.append("CNOT", [ancilla_qubit, j])
                elif pauli == 'Z':
                    circuit.append("CZ", [ancilla_qubit, j])
                elif pauli == 'Y':
                    circuit.append("S_DAG", j)
                    circuit.append("CNOT", [ancilla_qubit, j])
                    circuit.append("S", j)
            
            circuit.append_operation("M", [ancilla_qubit])
            circuit.append_operation("DETECTOR", [], [ancilla_qubit])
            circuit.append("H", ancilla_qubit)

        for q in range(num_data_qubits):
            circuit.append_operation("Z_ERROR", [q], p)

    circuit.append_operation("M", range(num_data_qubits))
    circuit.append_operation("OBSERVABLE_INCLUDE", [stim.target_rec(-q) for q in range(num_data_qubits, 0, -1)], 0)
    circuit.append_operation("OBSERVABLE_INCLUDE", [stim.target_rec(-q) for q in range(num_data_qubits, 0, -1)], 1)

    return circuit

def simulate_stim_circuit(circuit, num_shots):
    detector_sampler = circuit.compile_detector_sampler()
    detector_samples, observables = detector_sampler.sample(num_shots, separate_observables=True)
    return detector_samples, observables

def decode_outputs(circuit, detector_samples):
    decoder = BPOSD(
        circuit.detector_error_model(),
        max_bp_iters=20,
        bp_method="msl",
        osd_method="osd0",
        osd_order=0
    )
    predicted_observables = decoder.decode_batch(detector_samples)
    return predicted_observables

def calculate_error_rate(predicted_observables, observables):
    num_mistakes = np.sum(np.any(predicted_observables != observables, axis=1))
    error_rate = num_mistakes / len(observables)
    return error_rate, num_mistakes

def convert_to_stabilizers(x_part, z_part):
    if x_part.shape != z_part.shape:
        raise ValueError("x_part and z_part matrices must have the same shape")
    
    stabilizers = []
    for i in range(x_part.shape[0]):
        stabilizer = ''
        for j in range(x_part.shape[1]):
            if x_part[i, j] == 1 and z_part[i, j] == 0:
                stabilizer += 'X'
            elif x_part[i, j] == 0 and z_part[i, j] == 1:
                stabilizer += 'Z'
            elif x_part[i, j] == 1 and z_part[i, j] == 1:
                stabilizer += 'Y'
            else:
                stabilizer += 'I'
        stabilizers.append(stabilizer)
    return stabilizers

def main():
    # stabilizers = [
    #     "XIYZX",
    #     "ZIXYZ", 
    #     "IXXXX",
    #     "IZZZZ"
    # ]
    x_part = [
        [1, 0, 1, 0, 1],
        [0, 0, 1, 1, 0],
        [0, 1, 1, 1, 1],
        [0, 0, 0, 0, 0]
    ]
    
    z_part = [
        [0, 0, 1, 1, 0],
        [1, 0, 0, 1, 1],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1]
    ]
    x_part = np.array(x_part)
    z_part = np.array(z_part)
    stabilizers = convert_to_stabilizers(x_part, z_part)
    print(stabilizers)

    p = 0.07
    num_rounds = 10
    num_shots = 100

    circuit = generate_stim_circuit(stabilizers, p, num_rounds)
    print("Circuit:")
    print(circuit)

    detector_samples, observables = simulate_stim_circuit(circuit, num_shots)
    print("\nDetector Samples (first 5 shots):")
    for i in range(min(5, num_shots)):
        print(f"Shot {i+1}: {detector_samples[i]}")

    print("\nObservables (first 5 shots):")
    for i in range(min(5, num_shots)):
        print(f"Shot {i+1}: {observables[i]}")

    predicted_observables = decode_outputs(circuit, detector_samples)
    print("\nCorrections (first 5 shots):")
    for i in range(min(5, num_shots)):
        print(f"Shot {i+1}: {predicted_observables[i]}")

    error_rate, num_mistakes = calculate_error_rate(predicted_observables, observables)
    print(f"Error rate: {num_mistakes}/{num_shots} ({error_rate:.2%})")

if __name__ == "__main__":
    main()