import yaml
import os
import zipfile

def load_config(config_path):
    """
    Load configuration from a YAML file.
    """
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

# Function to zip the output folders
def zip_results(folders, zip_name):
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for folder in folders:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.join(folder, '..'))
                    zipf.write(file_path, arcname)
    print(f'Results zipped as {zip_name}')