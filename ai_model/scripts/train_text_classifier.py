"""
Train BERT-based fake news text classifier
Supports English and Tamil languages
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import torch
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
import pickle

# Paths
DATASET_DIR = Path("datasets/fake_news_text")
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

class FakeNewsDataset(torch.utils.data.Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

def load_data():
    """Load and prepare fake news dataset"""
    print("📂 Loading dataset...")
    
    # Load fake and real news
    fake_df = pd.read_csv(DATASET_DIR / "Fake.csv")
    true_df = pd.read_csv(DATASET_DIR / "True.csv")
    
    # Add labels
    fake_df['label'] = 0  # Fake
    true_df['label'] = 1  # Real
    
    # Combine
    df = pd.concat([fake_df, true_df], ignore_index=True)
    
    # Use title + text
    df['text'] = df['title'] + " " + df['text']
    
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"✅ Loaded {len(df)} articles")
    print(f"   - Fake: {len(fake_df)}")
    print(f"   - Real: {len(true_df)}")
    
    return df['text'].values, df['label'].values

def train_model():
    """Train BERT model for fake news detection"""
    print("\n🚀 Starting training...")
    
    # Load data
    texts, labels = load_data()
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42
    )
    
    print(f"\n📊 Dataset split:")
    print(f"   - Training: {len(X_train)}")
    print(f"   - Testing: {len(X_test)}")
    
    # Load tokenizer and model
    print("\n🤖 Loading BERT model...")
    tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
    model = BertForSequenceClassification.from_pretrained(
        'bert-base-multilingual-cased',
        num_labels=2
    )
    
    # Create datasets
    train_dataset = FakeNewsDataset(X_train, y_train, tokenizer)
    test_dataset = FakeNewsDataset(X_test, y_test, tokenizer)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=100,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
    )
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
    )
    
    # Train
    print("\n🏋️ Training model...")
    trainer.train()
    
    # Evaluate
    print("\n📈 Evaluating model...")
    results = trainer.evaluate()
    print(f"✅ Test Accuracy: {results['eval_loss']:.4f}")
    
    # Save model
    print("\n💾 Saving model...")
    model.save_pretrained(MODEL_DIR / "text_classifier_bert")
    tokenizer.save_pretrained(MODEL_DIR / "text_classifier_bert")
    
    print("\n✅ Training complete!")
    print(f"📁 Model saved to: {MODEL_DIR / 'text_classifier_bert'}")

if __name__ == "__main__":
    print("=" * 60)
    print("Fake News Text Classifier Training")
    print("=" * 60)
    train_model()
