import zipfile
import os

# Files and directories to include
INCLUDED_FILES = [
    'app.py',
    'database.py',
    'db_builder.py',
    'strategy.py',
    'requirements.txt',
    'run.bat',
    'README.txt',
    'fgo_full_data_jp.db'
]

INCLUDED_DIRS = [
    'templates',
    'static'
]

OUTPUT_FILENAME = 'FGO_Strategy_Room.zip'

def create_zip():
    print(f"Creating {OUTPUT_FILENAME}...")
    
    with zipfile.ZipFile(OUTPUT_FILENAME, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add individual files
        for filename in INCLUDED_FILES:
            if os.path.exists(filename):
                print(f"Adding: {filename}")
                zipf.write(filename)
            else:
                print(f"WARNING: File not found {filename}")
        
        # Add directories
        for dirname in INCLUDED_DIRS:
            if os.path.exists(dirname):
                print(f"Adding directory: {dirname}")
                for root, dirs, files in os.walk(dirname):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Keep directory structure
                        arcname = os.path.relpath(file_path, start='.')
                        print(f"  Adding: {arcname}")
                        zipf.write(file_path, arcname)
            else:
                print(f"WARNING: Directory not found {dirname}")
                
    print("\nZip creation complete!")
    print(f"File saved at: {os.path.abspath(OUTPUT_FILENAME)}")

if __name__ == "__main__":
    create_zip()
