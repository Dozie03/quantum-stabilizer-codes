const { spawn } = require('child_process');

const runSimulation = (req, res) => {
    const { model, errorRate, distances } = req.body;
    const python = spawn('python3', ['simulation/main.py', model, errorRate, distances.join(',')]);

    python.stdout.on('data', (data) => {
        res.json({ result: data.toString() });
    });

    python.stderr.on('data', (data) => {
        res.status(500).json({ error: data.toString() });
    });
};

module.exports = {
    runSimulation,
};
