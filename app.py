import os
from flask import Flask, request, render_template, send_from_directory # type: ignore
from werkzeug.utils import secure_filename
import uuid
import logging 
import shutil  # I WILL USE IT TO CLEAN THE UPLOADS FOLDER

# Import your existing processing function
from src.main import process_pdf
from src.utils import load_config

app = Flask(__name__)

# Load configuration
config = load_config('config/config.yaml')

# Path to output directory
output_dir = 'extracted_files'  # Path where results will be saved

# Process the PDF

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Max file size: 50MB

# Ensure the upload and output directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        try:
            # Check if the POST request has the file part
            if 'file' not in request.files:
                logging.warning("No file part in the request.")
                return render_template('index.html', message='No file part in the request')
            
            file = request.files['file']
            if file.filename == '':
                logging.warning("No file selected.")
                return render_template('index.html', message='No file selected')
            
            if file and allowed_file(file.filename):

                # Clear the "extracted_files" folder before saving the new file
                extracted_files_dir = 'extracted_files'
                if os.path.exists(extracted_files_dir):
                    shutil.rmtree(extracted_files_dir)  # Remove the entire directory and its contents
                os.makedirs(extracted_files_dir, exist_ok=True)  # Recreate the directory

                # Generate a unique filename to prevent collisions
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)

                # Process the uploaded file
                zip_file_path = process_pdf(file_path, output_dir)
                zip_filename = os.path.basename(zip_file_path)

                logging.info(f"File processed successfully: {zip_filename}")
                return render_template('index.html', message='File processed successfully', zip_filename=zip_filename)
            
            else:
                logging.warning("Invalid file type uploaded.")
                return render_template('index.html', message='Dear user, please try again and upload a valid PDF file.')
    
        except Exception as e:
            logging.error(f"An error occurred during processing: {e}")
            return render_template('index.html', message='An error occurred while processing the file.')
    
    else:
        return render_template('index.html')

@app.route('/download/<path:filename>')
def download_file(filename):
    # Ensure the filename is safe and does not include directory traversal characters
    filename = os.path.basename(filename)

    # these 4 lines are for debugging path issues:
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    print(f"Attempting to serve file from: {file_path}")
    
    if not os.path.exists(file_path):
        return render_template('index.html', message='File not found.')

    # Send the file as a download
    return send_from_directory(directory=app.config['OUTPUT_FOLDER'], path=filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
    