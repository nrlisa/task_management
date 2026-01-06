const jwt = require('jsonwebtoken');

// Mock Authentication - Replace with actual JWT verification logic
const authenticateUser = (req, res, next) => {
  const token = req.header('Authorization')?.replace('Bearer ', '');

  if (!token) return res.status(401).json({ error: 'Access Denied: No token provided.' });

  try {
    const verified = jwt.verify(token, process.env.JWT_SECRET || 'your_jwt_secret');
    req.user = verified;
    next();
  } catch (err) {
    res.status(400).json({ error: 'Invalid Token' });
  }
};

// Role Authorization Middleware
const requireRole = (role) => {
  return (req, res, next) => {
    if (!req.user || req.user.role !== role) {
      return res.status(403).json({ 
        error: 'Access Denied: Insufficient permissions.' 
      });
    }
    next();
  };
};

module.exports = { authenticateUser, requireRole };
