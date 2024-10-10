# Document Extraction Application

## Overview
This project processes scanned PDF documents, extracting text, images, tables, and charts into structured formats. It uses machine learning models for detection and OCR for text extraction.

## Features
- Supports different document types (forms, catalogs, financial reports)
- Extracts text, images, tables, and charts with captions
- Organizes output in a structured folder system
- Provides JSON files linking extracted elements

## Setup

### Prerequisites
- Python 3.7+
- pip (Python package installer)

### Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/pdf-extraction-app.git
    cd pdf-extraction-app
    ```

2. Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Download the necessary model weights and place them in the `models/` directory.

### Configuration
- Configure your settings in `config/config.yaml`. This file allows you to adjust DPI, output directories, OCR language, model paths, and class names.

### Running the Application
- To start the Flask application:
    ```bash
    python -m app
    ```
- Upload a PDF file through the web interface to process it.
- The application will process the file and provide a downloadable ZIP file containing the extracted content.
