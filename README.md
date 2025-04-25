# Lab Report Generator

A Flask web application that generates comprehensive lab reports from code files and lab instructions using the DeepSeek API.

## Features

- Upload lab instruction files (PDF or images) and code files (.py, .java, .c)
- Extract lab title and objectives from instruction files using OCR if needed
- Analyze code files using DeepSeek's API to provide detailed explanations
- Execute Python code and capture output and matplotlib visualizations
- Generate well-structured PDF reports with all the information
- Simple and intuitive user interface

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/lab-report-generator.git
   cd lab-report-generator
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```
   # Copy the example .env file
   cp .env.example .env
   # Edit the .env file with your DeepSeek API key
   ```

5. Install Tesseract OCR (required for text extraction from images):
   - Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
   - macOS: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`

6. Install Poppler (required for PDF processing):
   - Windows: Download and install from https://github.com/oschwartz10612/poppler-windows/releases/
   - macOS: `brew install poppler`
   - Linux: `sudo apt-get install poppler-utils`

## Usage

1. Start the Flask application:
   ```
   flask run
   ```

2. Open your web browser and navigate to `http://127.0.0.1:5000`

3. Upload your lab instruction file (PDF or image) and one or more code files

4. Click "Generate Report" and wait for the processing to complete

5. Download the generated PDF report

## Project Structure

```
lab-report-generator/
├── app.py                  # Flask application entry point
├── config.py               # Configuration settings
├── report_generator.py     # Report generation logic
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment variables
├── static/                 # Static assets
│   ├── css/                # CSS stylesheets
│   │   └── style.css       # Custom styles
│   └── js/                 # JavaScript files
│       └── script.js       # Client-side functionality
├── templates/              # HTML templates
│   ├── base.html           # Base template with layout
│   └── index.html          # Main page with upload form
└── uploads/                # Temporary file storage
```

## Dependencies

- Flask: Web framework
- DeepSeek API: For code analysis and explanation
- ReportLab: PDF generation
- pdf2image and pytesseract: OCR for instruction files
- matplotlib: For capturing Python visualizations

## Security Considerations

- The application runs Python code in a restricted environment
- Execution is limited to 30 seconds to prevent long-running processes
- File uploads are validated and restricted to specific file types
- Temporary files are stored in a separate directory

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
