const express = require('express');
const { auth, isAdmin } = require('../middleware/auth');
const User = require('../models/User');
const Analysis = require('../models/Analysis');

const router = express.Router();

// All admin routes require authentication and admin role
router.use(auth, isAdmin);

/**
 * @route   GET /api/admin/users
 * @desc    Get all users
 * @access  Admin
 */
router.get('/users', async (req, res) => {
  try {
    const { page = 1, limit = 20 } = req.query;

    const users = await User.find()
      .select('-password')
      .sort({ createdAt: -1 })
      .limit(limit * 1)
      .skip((page - 1) * limit);

    const count = await User.countDocuments();

    res.json({
      success: true,
      data: {
        users,
        totalPages: Math.ceil(count / limit),
        currentPage: page,
        total: count
      }
    });
  } catch (error) {
    console.error('Fetch users error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error fetching users' 
    });
  }
});

/**
 * @route   GET /api/admin/logs
 * @desc    Get all analysis logs
 * @access  Admin
 */
router.get('/logs', async (req, res) => {
  try {
    const { page = 1, limit = 50, type } = req.query;
    
    const query = type ? { type } : {};

    const logs = await Analysis.find(query)
      .populate('userId', 'name email')
      .sort({ createdAt: -1 })
      .limit(limit * 1)
      .skip((page - 1) * limit);

    const count = await Analysis.countDocuments(query);

    res.json({
      success: true,
      data: {
        logs,
        totalPages: Math.ceil(count / limit),
        currentPage: page,
        total: count
      }
    });
  } catch (error) {
    console.error('Fetch logs error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error fetching logs' 
    });
  }
});

/**
 * @route   GET /api/admin/stats
 * @desc    Get system statistics
 * @access  Admin
 */
router.get('/stats', async (req, res) => {
  try {
    // Total users
    const totalUsers = await User.countDocuments();
    const blockedUsers = await User.countDocuments({ isBlocked: true });

    // Total analyses
    const totalAnalyses = await Analysis.countDocuments();

    // Analyses by type
    const analysisByType = await Analysis.aggregate([
      { $group: { _id: '$type', count: { $sum: 1 } } }
    ]);

    // Most common fake topics (top suspicious words)
    const fakeNewsAnalyses = await Analysis.find({ 
      type: 'text',
      'result.prediction': 'fake'
    }).limit(100);

    const wordFrequency = {};
    fakeNewsAnalyses.forEach(analysis => {
      if (analysis.result.details?.suspiciousWords) {
        analysis.result.details.suspiciousWords.forEach(word => {
          wordFrequency[word] = (wordFrequency[word] || 0) + 1;
        });
      }
    });

    const topFakeTopics = Object.entries(wordFrequency)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([word, count]) => ({ word, count }));

    res.json({
      success: true,
      data: {
        totalUsers,
        blockedUsers,
        totalAnalyses,
        analysisByType,
        topFakeTopics
      }
    });
  } catch (error) {
    console.error('Fetch stats error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error fetching statistics' 
    });
  }
});

/**
 * @route   POST /api/admin/block/:userId
 * @desc    Block/unblock a user
 * @access  Admin
 */
router.post('/block/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const { block } = req.body; // true to block, false to unblock

    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({ 
        success: false, 
        message: 'User not found' 
      });
    }

    // Prevent blocking admin users
    if (user.role === 'admin') {
      return res.status(400).json({ 
        success: false, 
        message: 'Cannot block admin users' 
      });
    }

    user.isBlocked = block;
    await user.save();

    res.json({
      success: true,
      message: `User ${block ? 'blocked' : 'unblocked'} successfully`,
      data: { userId, isBlocked: user.isBlocked }
    });
  } catch (error) {
    console.error('Block user error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error updating user status' 
    });
  }
});

module.exports = router;
