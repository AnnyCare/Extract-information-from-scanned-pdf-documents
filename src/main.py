# Import necessary libraries
import torch
import os
import cv2
import pytesseract
from pytesseract import Output
# from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.logger import setup_logger
from detectron2 import model_zoo  # Ensure this is imported
import numpy as np
import json
import zipfile
from src.utils import load_config

config = load_config('config/config.yaml')


# Set the environment variable for torch cache
os.environ['TORCH_HOME'] = r'C:\Users\Public\pdfproject\torch_cache'

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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

# Setup logger
setup_logger()

# Define function to set up configuration and load the trained model
def setup_predictor():
    # Configure the model for inference
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml"))  # Adjust if your model config is different
    cfg.MODEL.WEIGHTS = config['model_weights_path']  # Path to your trained model
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.6  # Set threshold for inference
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = len(config['classes']['class_names'])  # Update based on your dataset's number of classes (7 in your case)
    cfg.MODEL.DEVICE = "cpu"  # Force using CPU
    return DefaultPredictor(cfg)


# Function to convert PDF pages to images
def convert_pdf_to_images(pdf_path):
    return convert_from_path(pdf_path)

# Define function to process a PDF and generate output
def process_pdf(pdf_path, output_dir):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load trained model
    predictor = setup_predictor()

    # Manually define class names as per your dataset
    class_names = config['classes']['class_names']
    text_classes = config['classes']['text_classes']
    image_classes = config['classes']['image_classes']

    # Create a folder for each class in the output directory
    for class_name in class_names:
        class_output_dir = os.path.join(output_dir, class_name)
        os.makedirs(class_output_dir, exist_ok=True)

    # Convert PDF to images
    images = convert_pdf_to_images(pdf_path)

    # Initialize text file and JSON structure
    ocr_text_file = os.path.join(output_dir, 'main.txt')
    json_output = []

    # Process each page in the PDF
    with open(ocr_text_file, 'w', encoding='utf-8') as ocr_file:
        for page_num, im in enumerate(images):
            # Convert PIL image to OpenCV format
            im = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)

            # Make predictions on the image
            outputs = predictor(im)
            instances = outputs["instances"].to("cpu")

            # JSON entry for the current page
            page_entry = {"page_number": page_num + 1, "instances": []}

            # Process each detected instance
            for i, box in enumerate(instances.pred_boxes):
                # Get the predicted class and corresponding label
                predicted_class = instances.pred_classes[i].item()
                class_name = class_names[predicted_class]

                # Get the bounding box for the instance
                bbox = box.numpy().astype(int).tolist()
                x1, y1, x2, y2 = bbox  # Unpack the bounding box coordinates

                # Extract the sub-image corresponding to the bounding box
                cropped_img = im[y1:y2, x1:x2]

                # Prepare instance entry for the JSON file
                instance_entry = {
                    "instance_id": i,
                    "class": class_name,
                    "bbox": bbox
                }

                if class_name in text_classes:
                    # Perform OCR on the cropped image
                    ocr_text = pytesseract.image_to_string(cropped_img, config='--psm 6')

                    # Write to the text file
                    ocr_file.write(f"Page {page_num + 1}, Instance {i}, Class: {class_name}\n")
                    ocr_file.write(ocr_text + "\n\n")

                    # Add OCR text to JSON
                    instance_entry["ocr_text"] = ocr_text
                elif class_name in image_classes:
                    # Save the cropped image
                    image_output_dir = os.path.join(output_dir, class_name)
                    output_image_path = os.path.join(image_output_dir, f"page_{page_num + 1}instance{i}.jpg")
                    cv2.imwrite(output_image_path, cropped_img)

                    # Write the image path to the text file
                    ocr_file.write(f"[Image saved at: {output_image_path}]\n\n")

                    # Add image path to JSON
                    instance_entry["image_path"] = output_image_path

                # Append the instance information to the page entry
                page_entry["instances"].append(instance_entry)

            # Append the page entry to the JSON output
            json_output.append(page_entry)

            print(f"Processed page {page_num + 1} of {len(images)}.")

    # Save the JSON output to a file
    json_file_path = os.path.join(output_dir, 'main.json')
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(json_output, json_file, indent=4)

    # Zip the results
    output_zip = os.path.join('outputs', f"{os.path.basename(pdf_path).replace('.pdf', '')}_output.zip")
    zip_results([output_dir], output_zip)

    print(f"OCR extraction and image saving completed. Text saved to {ocr_text_file} and JSON saved to {json_file_path}.")

    return output_zip

