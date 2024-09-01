const express = require('express');
const { runSimulation } = require('../controllers/quantumController');

const router = express.Router();

router.post('/simulate', runSimulation);

module.exports = router;
