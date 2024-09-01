import React, { useState } from 'react';

function InputForm({ onResult }) {
    const [model, setModel] = useState('Depolarizing');
    const [errorRate, setErrorRate] = useState(0.01);
    const [distances, setDistances] = useState('3,5,7');

    const handleSubmit = async (e) => {
        e.preventDefault();
        const response = await fetch('/api/quantum/simulate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ model, errorRate, distances: distances.split(',').map(Number) }),
        });
        const data = await response.json();
        onResult(data.result);
    };

    return (
        <form onSubmit={handleSubmit}>
            <div>
                <label>Model:</label>
                <select value={model} onChange={(e) => setModel(e.target.value)}>
                    <option value="Depolarizing">Depolarizing</option>
                    <option value="Amplitude Damping">Amplitude Damping</option>
                    <option value="Biased Noise">Biased Noise</option>
                </select>
            </div>
            <div>
                <label>Error Rate:</label>
                <input
                    type="number"
                    value={errorRate}
                    onChange={(e) => setErrorRate(e.target.value)}
                    step="0.01"
                    min="0"
                    max="1"
                />
            </div>
            <div>
                <label>Distances:</label>
                <input
                    type="text"
                    value={distances}
                    onChange={(e) => setDistances(e.target.value)}
                />
            </div>
            <button type="submit">Run Simulation</button>
        </form>
    );
}

export default InputForm;
