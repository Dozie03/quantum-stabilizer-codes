import stim
import numpy as np
from stimbposd import BPOSD

def generate_stim_circuit(stabilizers, p, num_rounds, logical_x):
    circuit = stim.Circuit()
    num_data_qubits = len(stabilizers[0])
    num_stabilizers = len(stabilizers)
    num_total_qubits = num_data_qubits + num_stabilizers

    # Define QUBIT_COORDS with only 2 parameters
    for i in range(num_data_qubits):
        circuit.append("QUBIT_COORDS", [i], [0, i])
    for i in range(num_stabilizers):
        circuit.append("QUBIT_COORDS", [num_data_qubits + i], [1, i])

    # Initialize all qubits
    circuit.append_operation("R", range(num_total_qubits))

    # Apply initial X errors to all qubits
    circuit.append_operation("X_ERROR", range(num_total_qubits), p)

    # Create the repeated part of the circuit
    for round in range(num_rounds):
        # Measure stabilizers
        for i, stabilizer in enumerate(stabilizers):
            ancilla = num_data_qubits + i
            circuit.append("H", ancilla)
            for j, pauli in enumerate(stabilizer):
                if pauli == 'X':
                    circuit.append("CX", [ancilla, j])
                elif pauli == 'Z':
                    circuit.append("CZ", [ancilla, j])
                elif pauli == 'Y':
                    circuit.append("CY", [ancilla, j])
            circuit.append("H", ancilla)
            circuit.append_operation("M", [ancilla])

        # Apply X errors to all qubits
        circuit.append_operation("X_ERROR", range(num_total_qubits), p)

        # Add DETECTOR for each stabilizer measurement
        if round == 0:  # First round
            for i in range(num_stabilizers):
                circuit.append("DETECTOR", [stim.target_rec(-1-i)], [1, i, 0])
        else:
            # Add SHIFT_COORDS before DETECTOR
            circuit.append("SHIFT_COORDS", [], [0, 0, 1])
            for i in range(num_stabilizers):
                circuit.append("DETECTOR", [
                    stim.target_rec(-1-i),
                    stim.target_rec(-1-i-num_stabilizers)
                ], [1, i, 0])

    # Measure data qubits at the end
    circuit.append_operation("M", range(num_data_qubits))

    # Add SHIFT_COORDS before final DETECTOR
    circuit.append("SHIFT_COORDS", [], [0, 0, 1])

    # Add final DETECTOR for each stabilizer
    for i in range(num_stabilizers):
        circuit.append("DETECTOR", [
            stim.target_rec(-1-i-num_data_qubits),
            stim.target_rec(-1-i-num_data_qubits-num_stabilizers)
        ], [1, i, 1])

    # Add OBSERVABLE_INCLUDE for logical X operator
    logical_x_indices = [i for i, x in enumerate(logical_x) if x == '1']
    circuit.append("OBSERVABLE_INCLUDE", [stim.target_rec(-i-1) for i in logical_x_indices], 0)

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
    num_rounds = 3
    num_shots = 100

    # circuit = generate_stim_circuit(stabilizers, p, num_rounds, '11111', '11111')
    circuit = generate_stim_circuit(stabilizers, p, num_rounds, '11111')
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
    print(f"\nError rate: {num_mistakes}/{num_shots} ({error_rate:.2%})")

if __name__ == "__main__":
    main()