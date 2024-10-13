import numpy as np
from qiskit.transpiler import CouplingMap


def get_valid_integer(prompt):
    while True:
        try:
            value = int(input(prompt))
            if value > 0:
                return value
            else:
                print("Please enter a positive integer.")
        except ValueError:
            print("Please enter a valid integer.")


def get_user_input(prompt):
    """Helper function to get valid integer input (0 or 1) or 'undo' from the user."""
    while True:
        user_input = input(prompt).strip().lower()
        if user_input in ['0', '1']:
            return int(user_input)
        elif user_input == 'z':
            return 'z'
        else:
            print("Please enter 0, 1, or 'undo' to undo the last input.")


def print_matrix(matrix):
    """Prints the matrix, showing 'X' for unspecified values."""
    n = matrix.shape[0]
    print("\nCurrent Adjacency Matrix:")
    for i in range(n):
        row = []
        for j in range(n):
            if i == j:  # Diagonal values always set to 0
                row.append('0')
            elif matrix[i][j] == -1:
                row.append('X')  # Show 'X' for unset values
            else:
                row.append(str(matrix[i][j]))
        print(" ".join(row))
    print()


def create_matrix(n, bidirectional):
    """Create an n x n adjacency matrix with user input. Cannot couple qubit with itself"""
    matrix = np.full((n, n), -1, dtype=int)  # Initialize with -1 for unspecified entries
    np.fill_diagonal(matrix, 0)  # Set diagonal elements to 0 (self-coupling is not allowed)
    pending_inputs = {(i, j) for i in range(n) for j in range(n) if i != j}  # Track pending input
    history = []  # Stack to store the history of inputs for undo

    while pending_inputs:
        print_matrix(matrix)

        # Select the first pending input to ask the user for
        i, j = min(pending_inputs)  # Get the first pending position

        user_input = get_user_input(
            f"Enter 1 if qubit {i} is connected to qubit {j}, otherwise 0 (or 'z' to revert the last input): ")

        if user_input == 'z':
            if history:
                # Undo the last input
                last_matrix = history.pop()  # Get the last state of the matrix
                matrix = last_matrix  # Restore the last state
                # Recalculate pending inputs based on the restored matrix
                pending_inputs = {(x, y) for x in range(n) for y in range(n) if x != y and matrix[x][y] == -1}
            else:
                print("No inputs to undo!")
        else:
            # Record the input in the history before modifying the matrix
            history.append(matrix.copy())  # Save the current state before making changes
            # Record the input in the matrix
            matrix[i][j] = user_input
            pending_inputs.remove((i, j))
            if bidirectional:
                # Ensure bidirectional symmetry
                matrix[j][i] = user_input
                pending_inputs.discard((j, i))  # Remove symmetric position from pending inputs

    return matrix


def matrix_to_coupling_map(matrix):
    """Converts an n x n matrix into a Qiskit coupling map."""
    coupling_list = []
    n, m = matrix.shape

    for i in range(n):
        for j in range(m):
            if matrix[i][j] == 1:
                coupling_list.append((i, j))

    return CouplingMap(couplinglist=coupling_list)


def main():
    print("Welcome to the matrix-to-coupling-map generator!")

    # Get matrix size from the user
    n = get_valid_integer("Enter the number of qubits (n x n matrix): ")

    # Ask if the graph is bidirectional
    bidirectional = input("Is the coupling map bidirectional (y/n)? ").strip().lower() == 'y'

    # Create the matrix based on the user's input
    print(f"\nPlease enter the adjacency matrix for a {'bidirectional' if bidirectional else 'directed'} graph:")
    matrix = create_matrix(n, bidirectional)

    print("\nThe adjacency matrix you entered:")
    print(matrix)
    coupling_map = matrix_to_coupling_map(matrix)

    print("\nCoupling Map Edges:", coupling_map.get_edges())
    return coupling_map

# run simulation

# main()
