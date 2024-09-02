from quantum_simulation import create_surface_code_circuit, simulate_with_noise
from error_models import depolarizing_error_model, amplitude_damping_error_model, biased_noise_model

# Function to calculate the logical error rate from the simulation results
def calculate_logical_error_rate(result, code_distance):
    counts = result.get_counts()  # Get the counts of measurement outcomes
    total_shots = sum(counts.values())  # Total number of shots (simulations)
    logical_error_rate = 0

    # Iterate over all outcomes and count those leading to logical errors
    for outcome, count in counts.items():
        if outcome.count('1') % code_distance != 0:
            logical_error_rate += count
    
    logical_error_rate /= total_shots  # Calculate the logical error rate
    return logical_error_rate

# Function to optimize the surface code by testing different distances and noise models
def optimize_surface_code(error_models, distances):
    optimal_distance = None
    minimal_error_rate = float('inf')  # Start with a high minimal error rate
    optimal_error_model = None

    # Iterate over each combination of code distance and error model
    for distance in distances:
        for model_name, model_func in error_models.items():
            qc = create_surface_code_circuit(distance)  # Create the circuit
            noise_model = model_func(distance)  # Get the noise model
            result = simulate_with_noise(qc, noise_model)  # Simulate the circuit with noise
            logical_error_rate = calculate_logical_error_rate(result, distance)  # Calculate the logical error rate

            # Check if this is the best configuration so far
            if logical_error_rate < minimal_error_rate:
                minimal_error_rate = logical_error_rate
                optimal_distance = distance
                optimal_error_model = model_name

    # Return the optimal distance, minimal error rate, and error model
    return optimal_distance, minimal_error_rate, optimal_error_model
