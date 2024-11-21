from qiskit import QuantumCircuit
import matplotlib.pyplot as plt
import stim
import random
from collections import defaultdict

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
           elif x_part[row][col] == 1 and z_part[row][col] == 1:
               qc.cy(row_qubit, col_qubit)

   for row in range(rows):
       qc.h(row)

   for row in range(rows):
       qc.measure(row, row)

   return qc

def advanced_gate_balancing(circuit):
   """Performs advanced gate balancing by merging gates, reordering qubits, and maximizing parallelism."""
   balanced_circuit = QuantumCircuit(circuit.num_qubits, circuit.num_clbits)
   gate_usage = defaultdict(int)

   # Step 1: Gate Merging and Commutation
   merged_circuit_data = []
   previous_gate = None
   for instruction in circuit.data:
       gate = instruction.operation
       qubits = instruction.qubits

       # Check if the current gate can be merged with the previous gate (e.g., two consecutive CNOTs)
       if previous_gate and previous_gate.operation == gate:
           continue  # Skip redundant gate
       merged_circuit_data.append(instruction)
       previous_gate = instruction

   # Step 2: Optimize qubit Reordering for Parallelism
   parallel_schedule = defaultdict(list)  # Track which qubits are used at each time step
   for instruction in merged_circuit_data:
       gate = instruction.operation
       qargs = instruction.qubits
       clbits = instruction.clbits

       qubits = [q._index for q in qargs]  # Get the qubit indices

       # Try to fit the gate into an available depth level, maximizing parallelism
       added_to_level = False
       for depth, gates in parallel_schedule.items():
           if not any(q in gates for q in qubits):  # No overlapping qubits
               parallel_schedule[depth].extend(qubits)  # Add qubits to that depth level
               if gate.name == 'measure':
                   balanced_circuit.append(gate, qargs, clbits)
               else:
                   balanced_circuit.append(gate, qargs)
               added_to_level = True
               break

       if not added_to_level:  # If no suitable parallel depth was found, add to a new depth level
           new_depth = len(parallel_schedule)
           parallel_schedule[new_depth].extend(qubits)
           if gate.name == 'measure':
               balanced_circuit.append(gate, qargs, clbits)
           else:
               balanced_circuit.append(gate, qargs)

   return balanced_circuit

def qiskit_to_stim(qc, title="Stim Circuit"):
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

   print(f"\n{title}:\n", "\n".join(stim_circuit), "\n")
   return "\n".join(stim_circuit)

def run_stim_simulation(string_circuit):
   circuit = stim.Circuit(string_circuit)
   simulator = stim.TableauSimulator()
   simulator.do(circuit)

   num_qubits = circuit.num_qubits
   num_shots = 100
   samples = []
   for _ in range(num_shots):
       single_sample = [simulator.measure(qubit) for qubit in range(num_qubits)]
       samples.append(single_sample)

   noisy_samples = []
   for sample in samples:
       noisy_sample = [1 - bit if random.uniform(0, 1) < 0.01 else bit for bit in sample]
       noisy_samples.append(noisy_sample)

   # Print samples vertically
   print("\nSimulation Results (Noisy Samples):")
   for sample in noisy_samples:
       print(sample)
   print("-" * 40)

def visualize_circuits(original_qc, balanced_qc):
   fig, axs = plt.subplots(2, 1, figsize=(10, 12))

   # Draw original circuit
   original_qc.draw(output='mpl', ax=axs[0])
   axs[0].set_title("Original Circuit")

   # Draw balanced circuit
   balanced_qc.draw(output='mpl', ax=axs[1])
   axs[1].set_title("Optimized Circuit")

   plt.tight_layout()
   plt.show()

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


   original_qc = generate_qiskit_circuit(x_part, z_part)

   # Convert to stim and print the initial circuit
   print("Before Gate Balancing:")
   stim_circuit_string = qiskit_to_stim(original_qc, title="Stim Circuit Before Gate Balancing")

   balanced_qc = advanced_gate_balancing(original_qc)

   print("After Gate Balancing:")
   stim_circuit_string_balanced = qiskit_to_stim(balanced_qc, title="Stim Circuit After Gate Balancing")

   run_stim_simulation(stim_circuit_string_balanced)

   # Visialize both circuits
   visualize_circuits(original_qc, balanced_qc)

   # Compare the depth before and after gate balancing
   original_depth = original_qc.depth()
   balanced_depth = balanced_qc.depth()

   print(f"\nOriginal Circuit Depth: {original_depth}")
   print(f"Optimized Circuit Depth: {balanced_depth}")
   print("-" * 40)
