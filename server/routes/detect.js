const express = require('express');
const multer = require('multer');
const axios = require('axios');
const { auth } = require('../middleware/auth');
const Analysis = require('../models/Analysis');

const router = express.Router();

// Configure multer for image and video uploads
const storage = multer.memoryStorage();
const upload = multer({ 
  storage,
  limits: { fileSize: 50 * 1024 * 1024 }, // 50MB limit
  fileFilter: (req, file, cb) => {
    if (file.mimetype.startsWith('image/') || file.mimetype.startsWith('video/')) {
      cb(null, true);
    } else {
      cb(new Error('Only image and video files are allowed'));
    }
  }
});

/**
 * @route   POST /api/detect/text
 * @desc    Detect fake news in text
 * @access  Private
 */
router.post('/text', auth, async (req, res) => {
  try {
    const { text, url, language = 'en' } = req.body;

    console.log('📝 Text detection request received');
    console.log('User ID:', req.user?._id);
    console.log('Text length:', text?.length || 0);
    console.log('URL:', url || 'none');

    if ((!text || text.trim().length === 0) && (!url || url.trim().length === 0)) {
      return res.status(400).json({ 
        success: false, 
        message: 'Text or URL is required' 
      });
    }

    // Call AI API for text analysis
    const aiResponse = await axios.post(`${process.env.AI_API_URL}/api/analyze/text`, {
      text,
      url,
      language
    });

    const result = aiResponse.data;
    console.log('🤖 AI Response received:', result.prediction, result.confidence);

    // Save analysis to database
    // Use URL or text for content (ensure it's not empty)
    const contentToSave = text ? text.substring(0, 500) : (url || 'URL analysis');
    
    console.log('💾 Attempting to save to MongoDB...');
    console.log('Content to save:', contentToSave.substring(0, 100));
    
    const analysis = new Analysis({
      userId: req.user._id,
      type: 'text',
      content: contentToSave,
      result: {
        prediction: result.prediction,
        confidence: result.confidence,
        details: {
          suspiciousWords: result.suspicious_words,
          language: result.detected_language,
          url: url || undefined
        }
      },
      language
    });
    
    try {
      await analysis.save();
      console.log('✅ Analysis saved to MongoDB:', analysis._id);
    } catch (saveError) {
      console.error('❌ Error saving analysis to MongoDB:', saveError);
      console.error('Save error details:', saveError.message);
      // Continue even if save fails
    }

    res.json({
      success: true,
      data: {
        prediction: result.prediction,
        confidence: result.confidence,
        suspiciousWords: result.suspicious_words,
        detectedLanguage: result.detected_language,
        explanation: result.explanation,
        sourceReliability: result.source_reliability,
        verification: result.verification,
        wikipediaVerification: result.wikipedia_verification,
        urlInfo: result.url_info,
        source_matches: result.source_matches || [],
        analysisId: analysis._id
      }
    });
  } catch (error) {
    console.error('Text detection error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error analyzing text',
      error: error.message
    });
  }
});

/**
 * @route   POST /api/detect/image
 * @desc    Detect deepfake in image or video
 * @access  Private
 */
router.post('/image', auth, upload.single('image'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ 
        success: false, 
        message: 'Image or video file is required' 
      });
    }

    console.log('🎬 Image detection request received');
    console.log('User ID:', req.user?._id);
    console.log('File name:', req.file.originalname);
    console.log('File size:', req.file.size);
    console.log('File type:', req.file.mimetype);

    const fileType = req.file.mimetype.startsWith('video') ? 'video' : 'image';

    // Send file to AI API
    const formData = new FormData();
    // Convert buffer to Blob for FormData
    const blob = new Blob([req.file.buffer], { type: req.file.mimetype });
    formData.append('image', blob, req.file.originalname);
    formData.append('fileType', fileType);

    console.log('📤 Sending to AI API...');

    const aiResponse = await axios.post(
      `${process.env.AI_API_URL}/api/analyze/image`,
      formData,
      {
        headers: {
          ...formData.getHeaders?.() || {},
          'Content-Type': 'multipart/form-data'
        }
      }
    );

    const result = aiResponse.data;
    console.log('🤖 AI Response received:', result.prediction, result.confidence);

    // Save analysis
    const analysis = new Analysis({
      userId: req.user._id,
      type: 'image',
      content: req.file.originalname,
      result: {
        prediction: result.prediction,
        confidence: result.confidence,
        details: {
          heatmapUrl: result.heatmap_url,
          fileType: fileType,
          fileSize: req.file.size
        }
      }
    });
    
    try {
      await analysis.save();
      console.log('✅ Image analysis saved to MongoDB:', analysis._id);
    } catch (saveError) {
      console.error('❌ Error saving image analysis to MongoDB:', saveError);
      // Continue even if save fails
    }

    res.json({
      success: true,
      data: {
        prediction: result.prediction,
        confidence: result.confidence,
        isDeepfake: result.is_deepfake,
        heatmapUrl: result.heatmap_url,
        method: result.method,
        analysisDetails: result.analysis_details || null,
        analysisId: analysis._id
      }
    });
  } catch (error) {
    console.error('Image detection error:', error);
    console.error('Error details:', error.response?.data || error.message);
    res.status(500).json({ 
      success: false, 
      message: 'Error analyzing image',
      error: error.message,
      details: error.response?.data
    });
  }
});

/**
 * @route   POST /api/detect/emotion-image
 * @desc    Analyze emotional manipulation from image (OCR + emotion analysis)
 * @access  Private
 */
router.post('/emotion-image', auth, upload.single('image'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ 
        success: false, 
        message: 'Image file is required' 
      });
    }

    const additionalText = req.body.additionalText || '';

    // Call AI API for emotion image analysis
    const formData = new FormData();
    const blob = new Blob([req.file.buffer], { type: req.file.mimetype });
    formData.append('image', blob, req.file.originalname);
    if (additionalText) {
      formData.append('additionalText', additionalText);
    }

    const aiResponse = await axios.post(
      `${process.env.AI_API_URL}/api/analyze/emotion-image`,
      formData,
      {
        headers: {
          ...formData.getHeaders?.() || {},
          'Content-Type': 'multipart/form-data'
        }
      }
    );

    const result = aiResponse.data;

    // Save analysis
    const analysis = new Analysis({
      userId: req.user._id,
      type: 'emotion-image',
      content: result.extracted_text?.substring(0, 500) || 'Image analysis',
      result: {
        prediction: result.manipulation_type,
        confidence: result.confidence,
        details: {
          manipulationScore: result.manipulation_score,
          triggeringWords: result.triggering_words,
          manipulationTechniques: result.manipulation_techniques,
          extractedText: result.extracted_text
        }
      }
    });
    
    try {
      await analysis.save();
      console.log('✅ Emotion image analysis saved to MongoDB:', analysis._id);
    } catch (saveError) {
      console.error('❌ Error saving emotion image analysis to MongoDB:', saveError);
    }

    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('Emotion image analysis error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error analyzing image',
      error: error.message
    });
  }
});

/**
 * @route   POST /api/detect/emotion
 * @desc    Analyze emotional manipulation from text
 * @access  Private
 */
router.post('/emotion', auth, async (req, res) => {
  try {
    const { text } = req.body;

    if (!text || text.trim().length === 0) {
      return res.status(400).json({ 
        success: false, 
        message: 'Text is required' 
      });
    }

    console.log('😡 Emotion analysis request received');
    console.log('Text length:', text.length);

    // Call AI API for emotion analysis
    const aiResponse = await axios.post(`${process.env.AI_API_URL}/api/analyze/emotion`, {
      text
    });

    const result = aiResponse.data;

    // Save analysis
    const analysis = new Analysis({
      userId: req.user._id,
      type: 'emotion',
      content: text.substring(0, 500),
      result: {
        prediction: result.manipulation_type,
        confidence: result.confidence,
        details: {
          manipulationScore: result.manipulation_score,
          triggeringWords: result.triggering_words,
          manipulationTechniques: result.manipulation_techniques
        }
      }
    });
    
    try {
      await analysis.save();
      console.log('✅ Emotion analysis saved to MongoDB:', analysis._id);
    } catch (saveError) {
      console.error('❌ Error saving emotion analysis to MongoDB:', saveError);
    }

    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('Emotion analysis error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error analyzing text',
      error: error.message
    });
  }
});

/**
 * @route   POST /api/detect/news-verify
 * @desc    Verify news against official sources (language-specific)
 * @access  Private
 */
router.post('/news-verify', auth, async (req, res) => {
  try {
    const { text, url, language = 'en' } = req.body;

    if (!text && !url) {
      return res.status(400).json({ 
        success: false, 
        message: 'Text or URL is required' 
      });
    }

    // Call AI API for news verification with language parameter
    const aiResponse = await axios.post(`${process.env.AI_API_URL}/api/news/verify-with-sources`, {
      text,
      url,
      language
    });

    const result = aiResponse.data;

    // Save analysis
    const analysis = new Analysis({
      userId: req.user._id,
      type: 'news-verification',
      content: text ? text.substring(0, 500) : (url || 'News verification'),
      result: {
        prediction: result.verification_status,
        confidence: result.credibility_score,
        details: {
          credibilityScore: result.credibility_score,
          matchingArticles: result.total_matches,
          sourcesCovered: result.sources_covered,
          entitiesFound: result.entities_found
        }
      }
    });
    
    try {
      await analysis.save();
      console.log('✅ News verification saved to MongoDB:', analysis._id);
    } catch (saveError) {
      console.error('❌ Error saving news verification to MongoDB:', saveError);
    }

    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('News verification error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error verifying news',
      error: error.message
    });
  }
});

/**
 * @route   POST /api/detect/news-search
 * @desc    Search for related news articles
 * @access  Private
 */
router.post('/news-search', auth, async (req, res) => {
  try {
    const { text, url, max_results = 10, language = 'en' } = req.body;

    if (!text && !url) {
      return res.status(400).json({ 
        success: false, 
        message: 'Text or URL is required' 
      });
    }

    // Call AI API for news search with language parameter
    const aiResponse = await axios.post(`${process.env.AI_API_URL}/api/news/search-related`, {
      text,
      url,
      max_results,
      language
    });

    const result = aiResponse.data;

    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('News search error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error searching for related news',
      error: error.message
    });
  }
});

module.exports = router;
