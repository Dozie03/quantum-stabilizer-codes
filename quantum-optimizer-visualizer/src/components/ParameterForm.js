import React, { useState } from 'react';

const ParameterForm = ({ onSubmit }) => {
  const [n, setN] = useState(5);
  const [k, setK] = useState(1);
  const [d, setD] = useState(3);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ n, k, d });
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="n">n (total number of qubits):</label>
        <input 
          type="number" 
          id="n" 
          value={n} 
          onChange={(e) => setN(parseInt(e.target.value))} 
          min="1"
        />
      </div>
      <div>
        <label htmlFor="k">k (number of logical qubits):</label>
        <input 
          type="number" 
          id="k" 
          value={k} 
          onChange={(e) => setK(parseInt(e.target.value))} 
          min="1"
        />
      </div>
      <div>
        <label htmlFor="d">d (code distance):</label>
        <input 
          type="number" 
          id="d" 
          value={d} 
          onChange={(e) => setD(parseInt(e.target.value))} 
          min="1"
        />
      </div>
      <button type="submit">Optimize</button>
    </form>
  );
};

export default ParameterForm;