from qiskit import QuantumCircuit
import matplotlib.pyplot as plt
import stim
import random

# Dictionary to map Qiskit gates to Stim gates
gate_mapping = {
    'h': 'H',       # Hadamard
    'x': 'X',       # Pauli-X
    'z': 'Z',       # Pauli-Z
    'cx': 'CNOT',   # CNOT
    'cz': 'CZ',     # CZ
    'measure': 'M'  # Measurement
}

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

def qiskit_to_stim(qc):
    """
    Converts a Qiskit QuantumCircuit into a stim circuit string.
    """
    stim_circuit = []
    
    # Iterate over the instructions in the Qiskit circuit
    for instruction in qc.data:
        gate = instruction.operation.name    # Gate name
        qubits = instruction.qubits          # Qubits the gate acts on
        
        # Get the corresponding stim gate from the mapping
        stim_gate = gate_mapping.get(gate.lower(), None)
        
        if stim_gate:
            # Extract the qubit indices using the correct _index attribute
            qubit_indices = [q._index for q in qubits]  # Use _index attribute
            
            # Build the stim gate string
            if len(qubit_indices) == 1:
                stim_circuit.append(f"{stim_gate} {qubit_indices[0]}")
            elif len(qubit_indices) > 1:
                stim_circuit.append(f"{stim_gate} {' '.join(map(str, qubit_indices))}")
    
    return "\n".join(stim_circuit)

def run_stim_simulation(string_circuit):
    # Create the stim circuit
    circuit = stim.Circuit(string_circuit)

    # Create a TableauSimulator for simulating the circuit
    simulator = stim.TableauSimulator()

    # Initialize the simulator with the circuit
    simulator.do(circuit)

    # Determine the number of qubits by checking the highest index in the circuit
    num_qubits = 0
    for instruction in circuit:
        for target in instruction.targets_copy():
            if target.is_qubit_target:
                num_qubits = max(num_qubits, target.value + 1)  # Adjust for 0-based indexing

    # Set the number of shots (samples)
    num_shots = 100

    # Collect samples by measuring each qubit individually for each shot
    samples = []
    for _ in range(num_shots):
        single_sample = []
        for qubit in range(num_qubits):
            measurement = simulator.measure(qubit)  # Measure each qubit individually
            single_sample.append(measurement)
        samples.append(single_sample)

    # Apply depolarizing noise manually to the samples
    noisy_samples = []
    for sample in samples:
        noisy_sample = []
        for bit in sample:
            # Add depolarizing noise with 1% probability
            if random.uniform(0, 1) < 0.01:  # Use Python's random.uniform for noise
                noisy_sample.append(1 - bit)  # Flip the bit (introduce noise)
            else:
                noisy_sample.append(bit)
        noisy_samples.append(noisy_sample)

    # Print the noisy samples
    print(noisy_samples)

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
    visualize_qiskit_circuit(qc)
    
    # Convert the Qiskit circuit to a Stim circuit string
    stim_circuit_string = qiskit_to_stim(qc)
    
    # Output the Stim circuit
    print("Stim Circuit:\n", stim_circuit_string)
    run_stim_simulation(stim_circuit_string)
