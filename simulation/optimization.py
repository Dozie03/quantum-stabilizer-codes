from quantum_simulation import create_surface_code_circuit, simulate_with_noise
from error_models import depolarizing_error_model, amplitude_damping_error_model, biased_noise_model

def calculate_logical_error_rate(result, code_distance):
    counts = result.get_counts()
    total_shots = sum(counts.values())
    logical_error_rate = 0
    for outcome, count in counts.items():
        if outcome.count('1') % code_distance != 0:
            logical_error_rate += count
    logical_error_rate /= total_shots
    return logical_error_rate

def optimize_surface_code(error_models, distances):
    optimal_distance = None
    minimal_error_rate = float('inf')
    optimal_error_model = None

    for distance in distances:
        for model_name, model_func in error_models.items():
            qc = create_surface_code_circuit(distance)
            noise_model = model_func(distance)
            result = simulate_with_noise(qc, noise_model)
            logical_error_rate = calculate_logical_error_rate(result, distance)
            if logical_error_rate < minimal_error_rate:
                minimal_error_rate = logical_error_rate
                optimal_distance = distance
                optimal_error_model = model_name

    return optimal_distance, minimal_error_rate, optimal_error_model
