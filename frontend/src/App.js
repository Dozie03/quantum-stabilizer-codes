import React, { useState } from 'react';
import Header from './components/Header';
import InputForm from './components/InputForm';
import ResultDisplay from './components/ResultDisplay';
import './App.css';

function App() {
    const [result, setResult] = useState(null);

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
