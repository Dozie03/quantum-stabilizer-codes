// Import required modules
const express = require('express');
const { runSimulation } = require('../controllers/quantumController');

// Create a new router instance
const router = express.Router();

// Define the route for running the quantum simulation
router.post('/simulate', runSimulation);

// Export the router for use in the app
module.exports = router;
