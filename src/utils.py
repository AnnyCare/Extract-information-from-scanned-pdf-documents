# src/utils.py

import os
import yaml

# src/utils.py

def create_output_dirs(base_path):
    """
    Create the required output directories.
    """
    folders = ['Text', 'Images', 'Tables', 'Charts', 'Metadata']
    for folder in folders:
        path = os.path.join(base_path, folder)
        os.makedirs(path, exist_ok=True)

def save_text(text_content, doc_name, page_num, output_base):
    """
    Save extracted text to a file.
    """
    text_folder = os.path.join(output_base, 'Text')
    os.makedirs(text_folder, exist_ok=True)
    text_filename = f'{doc_name}_page_{page_num}.txt'
    text_path = os.path.join(text_folder, text_filename)
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(text_content)
    return text_filename


def load_config(config_path):
    """
    Load configuration from a YAML file.
    """
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config
