import numpy as np
from error_Calculation import convert_to_stabilizers, generate_stim_circuit, simulate_stim_circuit, decode_outputs, calculate_error_rate
from gate_balancing import generate_qiskit_circuit, advanced_gate_balancing, qiskit_to_stim
from swap_gate_minimization import main as swap_gate_minimization
from qiskit import QuantumCircuit
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import json

def convert_to_json_serializable(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(v) for v in obj]
    else:
        return obj
    
# Global variables for n, k, d
n, k, d = 0, 0, 0

def get_user_input():
    global n, k, d
    while True:
        try:
            n = int(input("Enter n (total number of qubits): "))
            k = int(input("Enter k (number of logical qubits): "))
            d = int(input("Enter d (code distance): "))
            return n, k, d
        except ValueError:
            print("Please enter valid integers.")

def fetch_stabilizer_matrix(n, k):
    url = f"https://codetables.de/QECC/QECC.php?q=4&n={n}&k={k}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the pre tag containing the stabilizer matrix
    matrix_pre = soup.find('pre', string=lambda text: 'stabilizer matrix:' in text if text else False)
    
    if not matrix_pre:
        raise ValueError(f"No stabilizer matrix found for n={n}, k={k}")
    
    # Extract the matrix part
    matrix_text = matrix_pre.text.split('stabilizer matrix:')[1].strip()
    
    # print("Debug: Matrix text:")
    # print(matrix_text)
    
    # Parse the matrix
    rows = [row.strip() for row in matrix_text.split('\n') if '|' in row]
    
    # print("Debug: Parsed rows:")
    # for row in rows:
    #     print(row)
    
    return rows

def convert_to_x_z_parts(matrix):
    x_part = []
    z_part = []
    for row in matrix:
        # Remove square brackets and split by '|'
        x_str, z_str = row.strip('[]').split('|')
        x_row = [int(bit) for bit in x_str.split()]
        z_row = [int(bit) for bit in z_str.split()]
        x_part.append(x_row)
        z_part.append(z_row)
    return np.array(x_part), np.array(z_part)

def run_gate_balancing(x_part, z_part):
    qc = generate_qiskit_circuit(x_part, z_part)
    balanced_qc = advanced_gate_balancing(qc)
    return circuit_to_matrices(balanced_qc)

def run_swap_gate_minimization(x_part, z_part):
    global n
    optimized_qc = swap_gate_minimization(x_part, z_part, n)
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

def run_workflow(x_part, z_part, nn, kk, dd, num_iterations=25):
    global n, k, d

    n = nn
    k = kk
    d = dd

    global_minimum_error = float('inf')
    best_x_part = None
    best_z_part = None
    error_rates = []
    
    print(f"\nOptimizing [{n},{k},{d}] stabilizer code")
    print(f"Initial X part:\n{x_part}")
    print(f"Initial Z part:\n{z_part}")
    
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
        
        error_rates.append(current_error_rate)
        
        if current_error_rate < global_minimum_error:
            global_minimum_error = current_error_rate
            best_x_part = current_x_part.copy()
            best_z_part = current_z_part.copy()
            print(f"New minimum error rate: {global_minimum_error:.4f}")
            print(best_x_part)
            print(best_z_part)
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
    
    # Calculate improvement
    initial_error_rate = calculate_error_rate_for_matrices(x_part, z_part)
    improvement = (initial_error_rate - global_minimum_error) / initial_error_rate * 100
    print(f"\nImprovement: {improvement:.2f}%")
    
    # # Plot error rate progression
    # plt.figure(figsize=(10, 6))
    # plt.plot(range(1, num_iterations + 1), error_rates)
    # plt.title(f"Error Rate Progression for [{n},{k},{d}] Stabilizer Code")
    # plt.xlabel("Iteration")
    # plt.ylabel("Error Rate")
    # plt.grid(True)
    # plt.show()

    result = {
        "n": n,
        "k": k,
        "d": d,
        "final_error_rate": global_minimum_error,
        "best_x_part": best_x_part.tolist(),
        "best_z_part": best_z_part.tolist(),
        "improvement": improvement,
        "error_rates": error_rates,
        "iterations": num_iterations
    }
    
    # Convert the result to JSON-serializable format
    json_serializable_result = convert_to_json_serializable(result)
    
    return json_serializable_result

def circuit_to_matrices(qc: QuantumCircuit):
    global n
    num_data_qubits = n
    num_ancilla_qubits = qc.num_qubits - num_data_qubits
    x_part = np.zeros((num_ancilla_qubits, num_data_qubits), dtype=int)
    z_part = np.zeros((num_ancilla_qubits, num_data_qubits), dtype=int)

    for instruction in qc.data:
        if instruction.operation.name in ['cx', 'cz', 'cy']:
            control, target = instruction.qubits
            if control._index < num_ancilla_qubits:
                row = control._index
                col = target._index - num_ancilla_qubits
            else:
                row = target._index
                col = control._index - num_ancilla_qubits
            
            if 0 <= row < num_ancilla_qubits and 0 <= col < num_data_qubits:
                if instruction.operation.name == 'cx':
                    x_part[row][col] = 1
                elif instruction.operation.name == 'cz':
                    z_part[row][col] = 1
                elif instruction.operation.name == 'cy':
                    x_part[row][col] = 1
                    z_part[row][col] = 1

    return x_part, z_part

if __name__ == "__main__":
    # initial_x_part = np.array([
    #     [1, 0, 1, 0, 1],
    #     [0, 0, 1, 1, 0],
    #     [0, 1, 1, 1, 1],
    #     [0, 0, 0, 0, 0]
    # ])

    # initial_z_part = np.array([
    #     [0, 0, 1, 1, 0],
    #     [1, 0, 0, 1, 1],
    #     [0, 0, 0, 0, 0],
    #     [0, 1, 1, 1, 1]
    # ])

    n, k, d = get_user_input()
    # n,k,d = 5,1,3
    matrix = fetch_stabilizer_matrix(n, k)
    initial_x_part, initial_z_part = convert_to_x_z_parts(matrix)
    run_workflow(initial_x_part, initial_z_part, n, k, d, num_iterations=5)

    # print(run_swap_gate_minimization(initial_x_part, initial_z_part))

