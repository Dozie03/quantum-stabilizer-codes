from qiskit import QuantumCircuit
import matplotlib.pyplot as plt
import stim
import random
from bposd import bposd_decoder
import numpy as np


def calculate_syndrome(noisy_sample, stabilizer_matrix):
    """
    Calculates the syndrome for a given noisy sample by multiplying it with the stabilizer matrix.

    Args:
    - noisy_sample (np.ndarray): The noisy sample from the simulation.
    - stabilizer_matrix (np.ndarray): The stabilizer matrix used for the quantum code.

    Returns:
    - syndrome (np.ndarray): The syndrome vector.
    """
    # Calculate the syndrome by multiplying the sample by the stabilizer matrix and taking mod 2
    syndrome = np.dot(stabilizer_matrix, noisy_sample) % 2
    return syndrome


def decode_noisy_samples_bposd(noisy_samples, x_part, z_part):
    """
    Decodes noisy quantum samples using BposdDecoder and returns the corrected samples.

    Args:
    - noisy_samples (list): The noisy samples from the Stim simulation.
    - x_part (list): The X part of the stabilizer matrix.
    - z_part (list): The Z part of the stabilizer matrix.

    Returns:
    - corrected_samples: The decoded, corrected samples.
    """
    # Create the stabilizer matrix (combine x_part and z_part)
    stabilizer_matrix = np.concatenate((x_part, z_part), axis=1)

    # Initialize the BPOSD decoder
    decoder = bposd_decoder(stabilizer_matrix)

    corrected_samples = []

    # Convert noisy_samples to a NumPy array
    noisy_samples_np = np.array(noisy_samples)

    # Decode each noisy sample
    for sample in noisy_samples_np:
        # Calculate the syndrome for the noisy sample
        syndrome = calculate_syndrome(sample, stabilizer_matrix)

        # Decode the syndrome using the decoder
        decoded_sample = decoder.decode(syndrome)
        corrected_samples.append(decoded_sample)

    return corrected_samples


# Dictionary to map Qiskit gates to Stim gates
gate_mapping = {
    'h': 'H',  # Hadamard
    'x': 'X',  # Pauli-X
    'z': 'Z',  # Pauli-Z
    'cx': 'CNOT',  # CNOT
    'cz': 'CZ',  # CZ
    'measure': 'M'  # Measurement
}


def generate_qiskit_circuit(x_part, z_part):
    """
    Generates a Qiskit QuantumCircuit based on the input X and Z stabilizer matrices
    with the specified gate logic and measurements.
    """
    rows = len(x_part)  # Number of row qubits
    cols = len(x_part[0])  # Number of column qubits
    n_qubits = rows + cols + 1  # Adding 1 more qubit to match the expected 10
    n_classical_bits = rows  # Classical bits equal to the number of row qubits

    # Create a quantum circuit with n_qubits and n_classical_bits
    qc = QuantumCircuit(n_qubits, n_classical_bits)

    # Step 1: Place Hadamard gates on all row qubits
    for row in range(rows):
        qc.h(row)

    # Step 2: Apply CNOT, CZ, and CY gates based on the logic provided
    for row in range(rows):
        for col in range(cols):
            row_qubit = row  # Row qubits are in the first 'rows' qubits
            col_qubit = rows + col  # Column qubits start after row qubits

            if x_part[row][col] == 1 and z_part[row][col] == 0:
                qc.cx(row_qubit, col_qubit)  # CNOT gate
            elif x_part[row][col] == 0 and z_part[row][col] == 1:
                qc.cz(row_qubit, col_qubit)  # CZ gate
            elif x_part[row][col] == 1 and z_part[row][col] == 1:
                qc.cy(row_qubit, col_qubit)  # CY gate

    # Step 3: Add Hadamard gates on all row qubits again
    for row in range(rows):
        qc.h(row)

    # Step 4: Add measurement gates to all row qubits
    for row in range(rows):
        qc.measure(row, row)  # Measure row qubits into classical bits

    # Step 5: Ensure the extra qubit is used
    extra_qubit = n_qubits - 1
    qc.measure(extra_qubit, 0)  # You can measure the extra qubit or apply a dummy operation

    return qc




def visualize_qiskit_circuit(qc):
    """
    Visualizes a Qiskit QuantumCircuit using matplotlib.
    """
    qc.draw(output='mpl')
    plt.show()


def qiskit_to_stim(qc, depol1_prob=0.01, depol2_prob=0.02):
    """
    Converts a Qiskit QuantumCircuit into a stim circuit string with depolarizing noise.

    Args:
    - qc (QuantumCircuit): The Qiskit circuit.
    - depol1_prob (float): Probability for depolarizing noise on 1-qubit gates.
    - depol2_prob (float): Probability for depolarizing noise on 2-qubit gates.

    Returns:
    - str: A string representation of the stim circuit with depolarizing noise added.
    """
    stim_circuit = []

    # Iterate over the instructions in the Qiskit circuit
    for instruction in qc.data:
        gate = instruction.operation.name  # Gate name
        qubits = instruction.qubits  # Qubits the gate acts on

        # Get the corresponding stim gate from the mapping
        stim_gate = gate_mapping.get(gate.lower(), None)

        if stim_gate:
            # Extract the qubit indices
            qubit_indices = [q._index for q in qubits]  # Use _index attribute

            # Debugging output: print the gate and qubits being added
            print(f"Adding Stim Gate: {stim_gate}, Qubits: {qubit_indices}")

            # Build the stim gate string and add to the circuit
            if len(qubit_indices) == 1:
                stim_circuit.append(f"{stim_gate} {qubit_indices[0]}")
                # Add DEPOL1 for single-qubit gate (H)
                if stim_gate == 'H':
                    stim_circuit.append(f"DEPOLARIZE1({depol1_prob}) {qubit_indices[0]}")
            elif len(qubit_indices) == 2:
                stim_circuit.append(f"{stim_gate} {qubit_indices[0]} {qubit_indices[1]}")
                # Add DEPOL2 for two-qubit gates (CX, CZ, CY)
                if stim_gate in ['CNOT', 'CZ', 'CY']:
                    stim_circuit.append(f"DEPOLARIZE2({depol2_prob}) {qubit_indices[0]} {qubit_indices[1]}")

    return "\n".join(stim_circuit)



def run_stim_simulation(string_circuit, apply_noise=True):
    """
    Runs a simulation on the given stim circuit string and shows results both before and after applying noise.
    """
    # Create the stim circuit from the provided string
    circuit = stim.Circuit(string_circuit)

    # Create a TableauSimulator for simulating the circuit
    simulator_clean = stim.TableauSimulator()  # For clean simulation
    simulator_noisy = stim.TableauSimulator()  # For noisy simulation

    # Initialize both simulators with the circuit
    simulator_clean.do(circuit)
    simulator_noisy.do(circuit)

    # Determine the number of qubits in the circuit
    num_qubits = circuit.num_qubits  # Use stim's built-in method to get the number of qubits
    print(f"Number of qubits in the circuit: {num_qubits}")

    # Ensure the number of qubits matches the stabilizer matrix dimensions
    if num_qubits != 10:
        raise ValueError(f"Expected 10 qubits, but got {num_qubits}. Check the circuit generation.")

    # Set the number of shots (samples)
    num_shots = 1  # Run 100 shots for statistical results

    # 1. Run the clean simulation (before noise is applied)
    clean_samples = []
    for _ in range(num_shots):
        single_sample_clean = []
        for qubit in range(num_qubits):
            # Measure each qubit individually (clean simulation)
            measurement_clean = simulator_clean.measure(qubit)
            single_sample_clean.append(measurement_clean)
        clean_samples.append(single_sample_clean)

    # Print the clean samples
    print("\nClean Samples (Before Noise):")
    for sample in clean_samples:
        print(sample)

    # 2. If apply_noise is True, run the noisy simulation (after noise is applied)
    if apply_noise:
        noisy_samples = []
        for _ in range(num_shots):
            single_sample_noisy = []
            for qubit in range(num_qubits):
                # Measure each qubit individually (noisy simulation)
                measurement_noisy = simulator_noisy.measure(qubit)
                single_sample_noisy.append(measurement_noisy)
            noisy_samples.append(single_sample_noisy)

        # Print the noisy samples
        print("\nNoisy Samples (After Noise):")
        for sample in noisy_samples:
            print(sample)

    return clean_samples, noisy_samples if apply_noise else clean_samples



# Example usage
if __name__ == "__main__":
    # Example stabilizer matrix (X | Z)

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

    # Generate the Qiskit circuit based on stabilizer matrix
    qc = generate_qiskit_circuit(x_part, z_part)
    print(f"Qiskit Circuit Number of Qubits: {qc.num_qubits}")  # Debugging output to check qubit count

    # Visualize the Qiskit circuit
    visualize_qiskit_circuit(qc)

    # Convert the Qiskit circuit to a Stim circuit string with depolarizing noise
    stim_circuit_string = qiskit_to_stim(qc, depol1_prob=0.01, depol2_prob=0.02)

    # Output the Stim circuit
    print("Stim Circuit:\n", stim_circuit_string)

    # Run the simulation and get noisy samples
    _, noisy_samples = run_stim_simulation(stim_circuit_string)

    # Decode noisy samples using BPOSD
    corrected_samples = decode_noisy_samples_bposd(noisy_samples, x_part, z_part)

    # Output the corrected samples
    print("\nCorrected Samples (After Decoding):")
    for sample in corrected_samples:
        print(sample)
