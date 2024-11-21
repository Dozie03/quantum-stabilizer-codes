import React, { useState } from 'react';
import axios from 'axios';
import ParameterForm from './components/ParameterForm';
import OptimizationResults from './components/OptimizationResults';
import OptimizationCharts from './components/OptimizationCharts';
import './App.css';

function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleOptimize = async (params) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('/optimize', params);
      setResults(response.data);
    } catch (err) {
      console.error('Error details:', err.response?.data);
      setError('Error optimizing: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Quantum Stabilizer Code Optimizer</h1>
      <ParameterForm onSubmit={handleOptimize} />
      {loading && <p>Optimizing...</p>}
      {error && <p className="error">{error}</p>}
      {results && (
        <>
          <OptimizationResults results={results} />
          <OptimizationCharts results={results} />
        </>
      )}
    </div>
  );
}

export default App;