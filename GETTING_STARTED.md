# Getting Started with Lab Report Generator

This guide will help you set up and test the Lab Report Generator application.

## Prerequisites

Before you begin, make sure you have:

1. Python 3.8 or higher installed
2. A DeepSeek API key (sign up at https://platform.deepseek.com/)
3. Tesseract OCR installed (for text extraction from images)
4. Poppler installed (for PDF processing)

## Setup Instructions

1. **Create a virtual environment**:
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Set up your environment variables**:
   - Copy `.env.example` to `.env`
   - Edit `.env` and add your DeepSeek API key

4. **Run the application**:
   ```
   flask run
   ```

5. **Access the application**:
   Open your web browser and go to http://127.0.0.1:5000

## Testing the Application

The `test_files` directory contains sample files you can use to test the application:

1. **Sample Lab Instructions**: 
   - Convert `test_files/sample_lab_instructions.txt` to PDF using any online converter or word processor
   - Alternatively, you can take a screenshot of the text file and use it as an image

2. **Sample Code File**:
   - Use `test_files/sample_code.py` which contains a Fibonacci sequence implementation with matplotlib visualizations

3. **Testing Process**:
   - Upload the PDF/image of the lab instructions
   - Upload the sample code file
   - Check the "Execute Python code" option
   - Click "Generate Report"
   - Wait for processing to complete
   - Download and review the generated PDF report

## Troubleshooting

If you encounter issues:

1. **DeepSeek API errors**:
   - Verify your API key is correct
   - Check your DeepSeek account has sufficient credits

2. **OCR issues**:
   - Ensure Tesseract is properly installed and in your PATH
   - Try using clearer images or PDFs

3. **PDF generation problems**:
   - Verify all dependencies are installed correctly
   - Check the application logs for specific errors

4. **Python execution errors**:
   - Make sure the code doesn't require external dependencies not included in the requirements.txt
   - Check for syntax errors in the code

## Next Steps

Once you have the basic application working, you can:

1. Enhance the UI with more interactive elements
2. Add support for more programming languages
3. Implement user authentication for saving reports
4. Add more advanced code analysis features

## Support

If you need help, please open an issue on the GitHub repository or contact the maintainer.
