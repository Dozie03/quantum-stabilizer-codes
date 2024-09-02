// Import child_process module to run Python scripts
const { spawn } = require('child_process');

// Controller function to run the quantum simulation
const runSimulation = (req, res) => {
    // Extract parameters from the request body
    const { model, errorRate, distances } = req.body;

    // Spawn a child process to run the Python simulation script
    const python = spawn('python3', ['simulation/main.py', model, errorRate, distances.join(',')]);

    // Handle the output from the Python script and send it back to the client
    python.stdout.on('data', (data) => {
        res.json({ result: data.toString() });
    });

    // Handle any errors that occur during script execution
    python.stderr.on('data', (data) => {
        res.status(500).json({ error: data.toString() });
    });
};

// Export the runSimulation function for use in routes
module.exports = {
    runSimulation,
};
