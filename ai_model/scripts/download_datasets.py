"""
Download datasets from Kaggle for training
Run: python scripts/download_datasets.py
"""

import os
import zipfile
import subprocess
from pathlib import Path

# Create directories
DATASETS_DIR = Path("datasets")
DATASETS_DIR.mkdir(exist_ok=True)

def download_dataset(dataset_name, output_dir):
    """Download dataset from Kaggle"""
    print(f"\n📥 Downloading {dataset_name}...")
    try:
        subprocess.run([
            "kaggle", "datasets", "download", 
            "-d", dataset_name,
            "-p", str(output_dir)
        ], check=True)
        
        # Extract zip files
        for zip_file in output_dir.glob("*.zip"):
            print(f"📦 Extracting {zip_file.name}...")
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
            zip_file.unlink()  # Delete zip after extraction
        
        print(f"✅ {dataset_name} downloaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Error downloading {dataset_name}: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("Kaggle Dataset Downloader")
    print("=" * 60)
    
    # Check if Kaggle is configured
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if not kaggle_json.exists():
        print("\n❌ Kaggle API not configured!")
        print("Please follow these steps:")
        print("1. Go to https://www.kaggle.com/settings")
        print("2. Click 'Create New API Token'")
        print("3. Place kaggle.json in ~/.kaggle/")
        return
    
    datasets = [
        {
            "name": "clmentbisaillon/fake-and-real-news-dataset",
            "dir": DATASETS_DIR / "fake_news_text",
            "description": "Fake News Text Dataset"
        },
        {
            "name": "xhlulu/140k-real-and-fake-faces",
            "dir": DATASETS_DIR / "deepfake_images",
            "description": "Deepfake Images Dataset"
        },
        {
            "name": "kazanova/sentiment140",
            "dir": DATASETS_DIR / "sentiment",
            "description": "Sentiment Analysis Dataset"
        }
    ]
    
    print("\nDatasets to download:")
    for i, ds in enumerate(datasets, 1):
        print(f"{i}. {ds['description']}")
    
    print("\nStarting downloads...\n")
    
    success_count = 0
    for dataset in datasets:
        dataset["dir"].mkdir(exist_ok=True)
        if download_dataset(dataset["name"], dataset["dir"]):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Downloaded {success_count}/{len(datasets)} datasets successfully!")
    print("=" * 60)
    
    if success_count == len(datasets):
        print("\n🎉 All datasets ready for training!")
        print("Next step: Run training scripts")
        print("  python scripts/train_text_classifier.py")
        print("  python scripts/train_deepfake_detector.py")
        print("  python scripts/train_emotion_analyzer.py")
    else:
        print("\n⚠️ Some datasets failed to download.")
        print("Please check your Kaggle API configuration and try again.")

if __name__ == "__main__":
    main()
