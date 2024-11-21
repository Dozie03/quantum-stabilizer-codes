import React from 'react';

const OptimizationResults = ({ results }) => {
  const formatMatrix = (matrix) => {
    return (
      <table className="matrix">
        <tbody>
          {matrix.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {row.map((value, colIndex) => (
                <td key={colIndex}>{value}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  return (
    <div className="optimization-results">
      <h2>Optimization Results</h2>
      <p>Initial Parameters: n={results.n}, k={results.k}, d={results.d}</p>
      <p>Final minimum error rate: {results.final_error_rate.toFixed(4)}</p>
      <p>Improvement: {results.improvement.toFixed(2)}%</p>

      <div className="matrix-container">
        <div className="matrix-section">
          <h3>Best X Part</h3>
          {formatMatrix(results.best_x_part)}
        </div>

        <div className="matrix-section">
          <h3>Best Z Part</h3>
          {formatMatrix(results.best_z_part)}
        </div>
      </div>

      <h3>Error Rates</h3>
      <ul>
        {results.error_rates.map((rate, index) => (
          <li key={index}>
            Iteration {index + 1}: Error rate {rate.toFixed(4)}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default OptimizationResults;