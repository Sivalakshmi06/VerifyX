const express = require('express');
const PDFDocument = require('pdfkit');
const { auth } = require('../middleware/auth');
const Analysis = require('../models/Analysis');

const router = express.Router();

/**
 * @route   GET /api/dashboard/history
 * @desc    Get user's analysis history
 * @access  Private
 */
router.get('/history', auth, async (req, res) => {
  try {
    const { page = 1, limit = 10, type } = req.query;
    
    const query = { userId: req.user._id };
    if (type) query.type = type;

    const analyses = await Analysis.find(query)
      .sort({ createdAt: -1 })
      .limit(limit * 1)
      .skip((page - 1) * limit)
      .select('-__v');

    const count = await Analysis.countDocuments(query);

    res.json({
      success: true,
      data: {
        analyses,
        totalPages: Math.ceil(count / limit),
        currentPage: page,
        total: count
      }
    });
  } catch (error) {
    console.error('History fetch error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error fetching history' 
    });
  }
});

/**
 * @route   GET /api/dashboard/analytics
 * @desc    Get analytics data for dashboard
 * @access  Private
 */
router.get('/analytics', auth, async (req, res) => {
  try {
    const userId = req.user._id;

    // Total analyses by type
    const analysisByType = await Analysis.aggregate([
      { $match: { userId } },
      { $group: { _id: '$type', count: { $sum: 1 } } }
    ]);

    // Fake vs Real count for text analysis
    const textAnalysis = await Analysis.aggregate([
      { $match: { userId, type: 'text' } },
      { $group: { _id: '$result.prediction', count: { $sum: 1 } } }
    ]);

    // Recent activity (last 7 days)
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    
    const recentActivity = await Analysis.aggregate([
      { $match: { userId, createdAt: { $gte: sevenDaysAgo } } },
      { 
        $group: { 
          _id: { $dateToString: { format: '%Y-%m-%d', date: '$createdAt' } },
          count: { $sum: 1 }
        } 
      },
      { $sort: { _id: 1 } }
    ]);

    // Total count
    const totalAnalyses = await Analysis.countDocuments({ userId });

    res.json({
      success: true,
      data: {
        totalAnalyses,
        analysisByType,
        textAnalysis,
        recentActivity
      }
    });
  } catch (error) {
    console.error('Analytics fetch error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error fetching analytics' 
    });
  }
});

/**
 * @route   GET /api/dashboard/report/:id
 * @desc    Download PDF report for an analysis
 * @access  Private
 */
router.get('/report/:id', auth, async (req, res) => {
  try {
    const analysis = await Analysis.findOne({
      _id: req.params.id,
      userId: req.user._id
    }).populate('userId', 'name email');

    if (!analysis) {
      return res.status(404).json({ 
        success: false, 
        message: 'Analysis not found' 
      });
    }

    // Create PDF
    const doc = new PDFDocument();
    
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename=analysis-${analysis._id}.pdf`);
    
    doc.pipe(res);

    // PDF Content
    doc.fontSize(20).text('Fake News Detection Report', { align: 'center' });
    doc.moveDown();
    doc.fontSize(12).text(`Report ID: ${analysis._id}`);
    doc.text(`User: ${analysis.userId.name}`);
    doc.text(`Date: ${analysis.createdAt.toLocaleString()}`);
    doc.text(`Analysis Type: ${analysis.type.toUpperCase()}`);
    doc.moveDown();
    
    doc.fontSize(14).text('Analysis Results:', { underline: true });
    doc.moveDown();
    doc.fontSize(12).text(`Prediction: ${analysis.result.prediction}`);
    doc.text(`Confidence: ${(analysis.result.confidence * 100).toFixed(2)}%`);
    
    if (analysis.type === 'text' && analysis.result.details.suspiciousWords) {
      doc.moveDown();
      doc.text('Suspicious Words:');
      doc.text(analysis.result.details.suspiciousWords.join(', '));
    }
    
    if (analysis.type === 'emotion' && analysis.result.details.emotions) {
      doc.moveDown();
      doc.text('Emotional Analysis:');
      Object.entries(analysis.result.details.emotions).forEach(([emotion, score]) => {
        doc.text(`${emotion}: ${(score * 100).toFixed(2)}%`);
      });
    }
    
    doc.moveDown();
    doc.fontSize(10).text('Content Analyzed:');
    doc.text(analysis.content, { width: 500 });
    
    doc.end();
  } catch (error) {
    console.error('Report generation error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error generating report' 
    });
  }
});

module.exports = router;
