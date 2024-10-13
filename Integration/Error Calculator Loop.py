# transpile_circuit.py

from simulation import matrix_to_CouplingMap as mcm
from qiskit import transpile
# Function that generates the quantum circuit //Error corr team handle this
def get_circuit():
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.measure_all()
    return qc

# Function that returns the coupling map (connectivity) of the qubits
def get_coupling_map():
    mcm.main()

def main():
    # Step 1: Get the quantum circuit
    qc = get_circuit()

    # Step 2: Get the coupling map
    coupling_map = get_coupling_map()

    # Step 3: Transpile the circuit with the coupling map
    transpiled_circuit = transpile(qc, coupling_map=coupling_map)

    # Step 4: Print the transpiled circuit (optional)
    print("Transpiled Circuit:")
    print(transpiled_circuit)


if __name__ == "__main__":
    main()
