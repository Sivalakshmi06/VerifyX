const mongoose = require('mongoose');

const analysisSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  type: {
    type: String,
    enum: ['text', 'image', 'emotion', 'emotion-image', 'news-verification'],
    required: true
  },
  content: {
    type: String,
    required: true
  },
  result: {
    prediction: String,
    confidence: Number,
    details: mongoose.Schema.Types.Mixed
  },
  language: {
    type: String,
    default: 'en'
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

// Index for faster queries
analysisSchema.index({ userId: 1, createdAt: -1 });
analysisSchema.index({ type: 1 });

module.exports = mongoose.model('Analysis', analysisSchema);
