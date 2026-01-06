// c:\Users\Halim\Downloads\Telegram Desktop\task-management\routes\authRoutes.js

const express = require('express');
const authController = require('../controllers/authController');

const router = express.Router();

router.post('/register', authController.register);
router.post('/login', authController.login);
router.get('/logout', authController.logout);

module.exports = router;
