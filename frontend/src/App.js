import React, { useState } from 'react';
import Header from './components/Header';
import InputForm from './components/InputForm';
import ResultDisplay from './components/ResultDisplay';
import './App.css';

function App() {
    // State to hold the simulation result
    const [result, setResult] = useState(null);

    // Callback function to update the result state
    const handleResult = (data) => {
        setResult(data);
    };

    return (
        <div className="App">
            <Header />
            <InputForm onResult={handleResult} />
            {result && <ResultDisplay result={result} />}
        </div>
    );
}

export default App;
