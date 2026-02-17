import os
from pathlib import Path
import shutil

# Optional import - only needed for dataset downloading
try:
    import kagglehub
    HAS_KAGGLEHUB = True
except ImportError:
    HAS_KAGGLEHUB = False

def download_datasets():
    """Download required Kaggle datasets"""
    if not HAS_KAGGLEHUB:
        print("\n" + "="*50)
        print("ERROR: kagglehub is not installed")
        print("="*50)
        print("\nTo download datasets, please install kagglehub:")
        print("  pip install kagglehub")
        print("\nThen configure Kaggle API credentials:")
        print("  Set KAGGLE_USERNAME and KAGGLE_KEY environment variables")
        print("\nNote: This is optional - only needed for dataset downloading")
        print("The main application does NOT require kagglehub to run.")
        print("="*50 + "\n")
        return
    
    data_dir = Path("./data/kaggle_datasets")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    datasets = [
        "dikshaasinghhh/bajaj",  # Medical reports dataset
        "uciml/pima-indians-diabetes-database"  # Diabetes dataset
    ]
    
    print("\n" + "="*50)
    print("Kaggle Dataset Downloader")
    print("="*50)
    print("\nNote: Make sure kagglehub is installed and configured with API credentials")
    print("Install: pip install kagglehub")
    print("Configure: Set KAGGLE_USERNAME and KAGGLE_KEY environment variables\n")
    
    for dataset_name in datasets:
        print(f"\n{'='*50}")
        print(f"Downloading dataset: {dataset_name}")
        print(f"{'='*50}")
        try:
            path = kagglehub.dataset_download(dataset_name)
            print(f"[OK] Downloaded to: {path}")
            
            # Copy to our data directory structure
            dataset_folder = dataset_name.split("/")[-1]
            target_path = data_dir / dataset_folder
            
            if os.path.exists(path):
                if target_path.exists():
                    print(f"  -> Dataset already exists at {target_path}, skipping copy...")
                else:
                    shutil.copytree(path, target_path)
                    print(f"[OK] Copied to: {target_path}")
            else:
                print(f"[ERROR] Download path does not exist: {path}")
                
        except Exception as e:
            print(f"[ERROR] Failed to download {dataset_name}: {e}")
            print(f"  Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*50}")
    print("Dataset download process completed!")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    download_datasets()
