const express = require('express');
const mongoose = require('mongoose');
const cookieParser = require('cookie-parser');
const csrf = require('csurf');
const taskRoutes = require('./routes/taskRoutes');
const authRoutes = require('./routes/authRoutes');

const app = express();

// Middleware to parse JSON
app.use(express.json());
app.use(cookieParser());
app.use(express.static('public'));

// CSRF Protection: Enable for all state-changing requests
const csrfProtection = csrf({
  cookie: {
    httpOnly: true,
    secure: true
  }
});
app.use(csrfProtection);

// Database Connection
mongoose.connect('mongodb://localhost:27017/your_db_name')
  .then(() => console.log('MongoDB Connected'))
  .catch(err => console.error(err));

// Route to get CSRF Token (Frontend needs this for POST requests)
app.get('/api/csrf-token', (req, res) => {
  res.json({ csrfToken: req.csrfToken() });
});

// Register Routes
app.use('/api/auth', authRoutes);
app.use('/api/tasks', taskRoutes);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
