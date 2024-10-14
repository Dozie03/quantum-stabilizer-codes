from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap
import matplotlib.pyplot as plt
import stim
import random

# Dictionary to map Qiskit gates to Stim gates
gate_mapping = {
    'h': 'H',
    'x': 'X',
    'z': 'Z',
    'cx': 'CNOT',
    'cz': 'CZ',
    'measure': 'M'
}

def create_fully_connected_coupling_map(num_qubits):
    """Creates a fully connected coupling map for a given number of qubits."""
    return CouplingMap(couplinglist=[(i, j) for i in range(num_qubits) for j in range(i + 1, num_qubits)])

def compute_qubit_usage(matrix):
    """Returns the number of times each qubit (column) is used."""
    usage_count = [sum(col) for col in zip(*matrix)]
    return usage_count

def compute_stabilizer_weight(matrix):
    """Returns the weight of each stabilizer (row)."""
    stabilizer_weights = [sum(row) for row in matrix]
    return stabilizer_weights

def generate_qiskit_circuit(x_part, z_part):
    rows = len(x_part)
    cols = len(x_part[0])
    n_qubits = rows + cols
    n_classical_bits = rows

    qc = QuantumCircuit(n_qubits, n_classical_bits)

    for row in range(rows):
        qc.h(row)

    for row in range(rows):
        for col in range(cols):
            row_qubit = row
            col_qubit = rows + col
            if x_part[row][col] == 1 and z_part[row][col] == 0:
                qc.cx(row_qubit, col_qubit)
            elif x_part[row][col] == 0 and z_part[row][col] == 1:
                qc.cz(row_qubit, col_qubit)

    for row in range(rows):
        qc.h(row)

    for row in range(rows):
        qc.measure(row, row)

    return qc

def count_swap_gates(circuit):
    return sum(1 for gate in circuit.data if gate.operation.name == 'swap')

def qiskit_to_stim(qc):
    stim_circuit = []
    for instruction in qc.data:
        gate = instruction.operation.name
        qubits = instruction.qubits
        stim_gate = gate_mapping.get(gate.lower(), None)
        if stim_gate:
            qubit_indices = [q._index for q in qubits]
            if len(qubit_indices) == 1:
                stim_circuit.append(f"{stim_gate} {qubit_indices[0]}")
            elif len(qubit_indices) > 1:
                stim_circuit.append(f"{stim_gate} {' '.join(map(str, qubit_indices))}")
    return "\n".join(stim_circuit)

def run_stim_simulation(string_circuit):
    circuit = stim.Circuit(string_circuit)
    simulator = stim.TableauSimulator()
    simulator.do(circuit)

    num_qubits = max(target.value for instruction in circuit for target in instruction.targets_copy() if target.is_qubit_target) + 1
    num_shots = 100

    samples = []
    for _ in range(num_shots):
        sample = [simulator.measure(qubit) for qubit in range(num_qubits)]
        noisy_sample = [1 - bit if random.uniform(0, 1) < 0.01 else bit for bit in sample]
        samples.append(noisy_sample)

    print(samples)

def visualize_circuits(qc, optimized_qc):
    fig, axs = plt.subplots(2, 1, figsize=(10, 12))
    qc.draw(output='mpl', ax=axs[0])
    axs[0].set_title("Original Circuit (Before Optimization)")
    optimized_qc.draw(output='mpl', ax=axs[1])
    axs[1].set_title("Optimized Circuit (After Optimization)")
    plt.tight_layout()
    plt.show()

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
    
    # Compute proxy metrics based on Tanner graph analysis
    qubit_usage = compute_qubit_usage(x_part + z_part)
    stabilizer_weights = compute_stabilizer_weight(x_part + z_part)

    print(f"Qubit Usage: {qubit_usage}")
    print(f"Stabilizer Weights: {stabilizer_weights}")
    
    qc = generate_qiskit_circuit(x_part, z_part)
    
    num_qubits = 9  # Adjust to match your circuit
    coupling_map = create_fully_connected_coupling_map(num_qubits)  # Fully connected map
    
    for level in range(4):
        print(f"\nRunning with optimization level {level}...")
        optimized_qc = transpile(qc, coupling_map=coupling_map, optimization_level=level)

        original_swap_count = count_swap_gates(qc)
        optimized_swap_count = count_swap_gates(optimized_qc)

        visualize_circuits(qc, optimized_qc)

        stim_circuit_string = qiskit_to_stim(optimized_qc)
        print("Stim Circuit:\n", stim_circuit_string)

        run_stim_simulation(stim_circuit_string)

        original_depth = qc.depth()
        optimized_depth = optimized_qc.depth()

        print(f"Original Circuit Depth: {original_depth}, Optimized Circuit Depth: {optimized_depth}")
        print(f"Original SWAP Gates: {original_swap_count}, Optimized SWAP Gates: {optimized_swap_count}")
        print(f"Qubit Usage: {qubit_usage}")
        print(f"Stabilizer Weights: {stabilizer_weights}")

if __name__ == "__main__":
    main()

