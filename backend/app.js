// Import required modules
const express = require('express');
const quantumRoutes = require('./routes/quantumRoutes');

// Initialize Express app
const app = express();
app.use(express.json()); // Middleware to parse JSON bodies

// Use quantum routes for API
app.use('/api/quantum', quantumRoutes);

// Define server port and start listening
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
