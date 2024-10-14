from qiskit import QuantumCircuit
import matplotlib.pyplot as plt
import stim
import random
from bposd import bposd_decoder
import numpy as np

def decode_noisy_samples(result, x_part, z_part):
    num_shots, num_qubits = result.shape
    stabilizer_matrix = np.concatenate((x_part, z_part), axis=1)

    # Step 1: Calculate the frequency of 0's and 1's for each qubit across all shots
    syndrome_counts = np.sum(result, axis=0)  # Sum across all shots (rows)

    # Step 2: Apply majority voting to create a consensus syndrome
    # If more than half of the shots resulted in '1', then the consensus for that qubit is 1
    consensus_syndrome = (syndrome_counts > (num_shots / 2)).astype(int)

    # Step 3: Set up the BPOSD decoder
    decoder = bposd_decoder(stabilizer_matrix)

    # Step 4: Decode the consensus syndrome using the decoder
    correction = decoder.decode(consensus_syndrome)

    print("Consensus Syndrome:", consensus_syndrome)
    print("Correction:", correction)






# Dictionary to map Qiskit gates to Stim gates
gate_mapping = {
    'h': 'H',       # Hadamard
    'x': 'X',       # Pauli-X
    'z': 'Z',       # Pauli-Z
    'cx': 'CNOT',   # CNOT
    'cz': 'CZ',     # CZ
    'measure': 'M'  # Measurement
}

# def generate_qiskit_circuit(x_part, z_part):
#     """
#     Generates a Qiskit QuantumCircuit based on the input X and Z stabilizer matrices
#     with the specified gate logic and measurements.
#     """
#     rows = len(x_part)     # Number of row qubits
#     cols = len(x_part[0])  # Number of column qubits
#     n_qubits = rows + cols  # Total qubits = rows + columns
#     n_classical_bits = rows  # Classical bits equal to the number of row qubits
#     # n_classical_bits = n_qubits  
#     # Create a quantum circuit with n_qubits and n_classical_bits
#     qc = QuantumCircuit(n_qubits, n_classical_bits)

#     # Step 1: Place Hadamard gates on all row and col qubits
#     for qubit in range(n_qubits):
#         qc.h(qubit)

#     # Step 2: Apply CNOT, CZ, and CY gates based on the logic provided
#     for row in range(rows):
#         for col in range(cols):
#             row_qubit = row  # Row qubits are in the first 'rows' qubits
#             col_qubit = rows + col  # Column qubits start after row qubits

#             if x_part[row][col] == 1 and z_part[row][col] == 0:
#                 qc.cx(row_qubit, col_qubit)  # CNOT gate
#             elif x_part[row][col] == 0 and z_part[row][col] == 1:
#                 qc.cz(row_qubit, col_qubit)  # CZ gate
#             elif x_part[row][col] == 1 and z_part[row][col] == 1:
#                 qc.cy(row_qubit, col_qubit)  # CY gate

#     # Step 3: Add Hadamard gates on all row and col qubits again
#     for qubit in range(n_qubits):
#         qc.h(qubit)

#     # Step 4: Add measurement gates to all row qubits
#     for qubit in range(n_qubits):
#         qc.measure(qubit, qubit)  # Measure row qubits into classical bits

#     return qc

def generate_qiskit_circuit(x_part, z_part):
    """
    Generates a Qiskit QuantumCircuit based on the input X and Z stabilizer matrices
    with the specified gate logic and measurements.
    """
    rows = len(x_part)     # Number of row qubits
    cols = len(x_part[0])  # Number of column qubits
    n_qubits = rows + cols  # Total qubits = rows + columns
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
        qubits = instruction.qubits        # Qubits the gate acts on
        
        # Get the corresponding stim gate from the mapping
        stim_gate = gate_mapping.get(gate.lower(), None)
        
        if stim_gate:
            # Extract the qubit indices
            qubit_indices = [q._index for q in qubits]  # Use _index attribute

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

def run_stim_simulation(string_circuit):
    """
    Runs a simulation on the given stim circuit string and shows results both before and after applying noise.
    """
    # Create a STIM circuit from the input string
    circuit = stim.Circuit(stim_circuit_string)
    
    # Run the circuit and sample 'num_shots' times
    num_shots = 100
    sampler = circuit.compile_sampler()
    # Use the sampler to generate samples
    result = sampler.sample(num_shots)
    
    return result


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
    
    # Visualize the Qiskit circuit
    # visualize_qiskit_circuit(qc)
    
    # Convert the Qiskit circuit to a Stim circuit string with depolarizing noise
    stim_circuit_string = qiskit_to_stim(qc, depol1_prob=0.01, depol2_prob=0.02)
    
    # Output the Stim circuit
    print("Stim Circuit:\n", stim_circuit_string)
    
    # Run the simulation and get noisy samples
    noisy_samples = run_stim_simulation(stim_circuit_string)
    print("Samples: \n", noisy_samples, '\n')
    
    decode_noisy_samples(noisy_samples, x_part, z_part)
