import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const OptimizationCharts = ({ results }) => {
  const chartData = results.error_rates.map((rate, index) => ({
    iteration: index + 1,
    errorRate: rate,
  }));

  return (
    <div className="optimization-charts">
      <h2>Optimization Progress</h2>
      <LineChart width={600} height={300} data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="iteration" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="errorRate" stroke="#8884d8" name="Error Rate" />
      </LineChart>
    </div>
  );
};

export default OptimizationCharts;