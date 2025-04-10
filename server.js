const express = require('express');
const app = express();

// Optional middleware
app.use(express.json());

// Basic route
app.get('/', (req, res) => {
  res.send('✅ Hello from Railway!');
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
