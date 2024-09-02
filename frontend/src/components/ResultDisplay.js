import React from 'react';

// Component to display the simulation result
function ResultDisplay({ result }) {
    return (
        <div>
            <h3>Simulation Result</h3>
            <pre>{result}</pre> {/* Display result in a preformatted text block */}
        </div>
    );
}

export default ResultDisplay;
