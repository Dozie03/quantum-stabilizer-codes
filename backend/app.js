const express = require('express');
const quantumRoutes = require('./routes/quantumRoutes');

const app = express();
app.use(express.json());

app.use('/api/quantum', quantumRoutes);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
