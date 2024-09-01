import sys
from optimization import optimize_surface_code
from error_models import depolarizing_error_model, amplitude_damping_error_model, biased_noise_model

if __name__ == "__main__":
    model = sys.argv[1]
    error_rate = float(sys.argv[2])
    distances = [int(d) for d in sys.argv[3].split(',')]

    error_models = {
        'Depolarizing': lambda d: depolarizing_error_model(error_rate, d ** 2),
        'Amplitude Damping': lambda d: amplitude_damping_error_model(error_rate, d ** 2),
        'Biased Noise': lambda d: biased_noise_model(error_rate, error_rate, d ** 2)
    }

    optimal_distance, minimal_error_rate, _ = optimize_surface_code(error_models, distances)
    print(f"Optimal Code Distance: {optimal_distance}")
    print(f"Minimal Logical Error Rate: {minimal_error_rate:.6f}")
