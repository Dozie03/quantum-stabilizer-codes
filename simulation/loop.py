import numpy as np
from error_Calculation import convert_to_stabilizers, generate_stim_circuit, simulate_stim_circuit, decode_outputs, calculate_error_rate
from gate_balancing import generate_qiskit_circuit, advanced_gate_balancing, qiskit_to_stim
from swap_gate_minimization import main as swap_gate_minimization
from qiskit import QuantumCircuit

def run_gate_balancing(x_part, z_part):
    qc = generate_qiskit_circuit(x_part, z_part)
    balanced_qc = advanced_gate_balancing(qc)
    return circuit_to_matrices(balanced_qc)

def run_swap_gate_minimization(x_part, z_part):
    # qc = generate_qiskit_circuit(x_part, z_part)
    optimized_qc = swap_gate_minimization(x_part, z_part)
    return circuit_to_matrices(optimized_qc)

def calculate_error_rate_for_matrices(x_part, z_part):
    stabilizers = convert_to_stabilizers(x_part, z_part)
    p = 0.07
    num_rounds = 10
    num_shots = 100
    
    circuit = generate_stim_circuit(stabilizers, p, num_rounds)
    detector_samples, observables = simulate_stim_circuit(circuit, num_shots)
    predicted_observables = decode_outputs(circuit, detector_samples)
    error_rate, num_mistakes = calculate_error_rate(predicted_observables, observables)
    
    return error_rate

def run_workflow(x_part, z_part, num_iterations=2):
    global_minimum_error = float('inf')
    best_x_part = None
    best_z_part = None

    for i in range(num_iterations):
        print(f"\nIteration {i+1}:")
        
        # Run gate balancing
        gb_x_part, gb_z_part = run_gate_balancing(x_part, z_part)
        gb_error_rate = calculate_error_rate_for_matrices(gb_x_part, gb_z_part)
        print(f"Gate balancing error rate: {gb_error_rate:.4f}")

        # Run swap gate minimization
        sgm_x_part, sgm_z_part = run_swap_gate_minimization(x_part, z_part)
        sgm_error_rate = calculate_error_rate_for_matrices(sgm_x_part, sgm_z_part)
        print(f"Swap gate minimization error rate: {sgm_error_rate:.4f}")

        # Compare error rates and update if necessary
        if gb_error_rate < sgm_error_rate:
            current_error_rate = gb_error_rate
            current_x_part = gb_x_part
            current_z_part = gb_z_part
            print("Gate balancing performed better")
        else:
            current_error_rate = sgm_error_rate
            current_x_part = sgm_x_part
            current_z_part = sgm_z_part
            print("Swap gate minimization performed better")

        if current_error_rate < global_minimum_error:
            global_minimum_error = current_error_rate
            best_x_part = current_x_part.copy()
            best_z_part = current_z_part.copy()
            print(f"New minimum error rate: {global_minimum_error:.4f}")
        else:
            print(f"Current minimum error rate: {global_minimum_error:.4f}")

        # Use the better matrices for the next iteration
        x_part = current_x_part
        z_part = current_z_part

    print(f"\nFinal minimum error rate: {global_minimum_error:.4f}")
    print("Best x_part:")
    print(best_x_part)
    print("Best z_part:")
    print(best_z_part)

def circuit_to_matrices(qc: QuantumCircuit):
    num_rows = qc.num_qubits // 2
    num_cols = qc.num_qubits - num_rows
    x_part = np.zeros((num_rows, num_cols), dtype=int)
    z_part = np.zeros((num_rows, num_cols), dtype=int)

    for instruction in qc.data:
        if instruction.operation.name in ['cx', 'cz', 'cy']:
            control, target = instruction.qubits
            row = control._index if control._index < num_rows else target._index
            col = target._index - num_rows if target._index >= num_rows else control._index - num_rows
            
            if instruction.operation.name == 'cx':
                x_part[row][col] = 1
            elif instruction.operation.name == 'cz':
                z_part[row][col] = 1
            elif instruction.operation.name == 'cy':
                x_part[row][col] = 1
                z_part[row][col] = 1

    return x_part, z_part

if __name__ == "__main__":
    initial_x_part = np.array([
        [1, 0, 1, 0, 1],
        [0, 0, 1, 1, 0],
        [0, 1, 1, 1, 1],
        [0, 0, 0, 0, 0]
    ])

    initial_z_part = np.array([
        [0, 0, 1, 1, 0],
        [1, 0, 0, 1, 1],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1]
    ])

    run_workflow(initial_x_part, initial_z_part, num_iterations=25)