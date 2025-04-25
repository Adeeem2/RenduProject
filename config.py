import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Configuration settings for the Flask application."""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
    ALLOWED_EXTENSIONS = {
        'instruction': {'pdf', 'png', 'jpg', 'jpeg'},
        'code': {'py', 'java', 'c', 'ipynb'}
    }

    # DeepSeek API settings
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
    if not DEEPSEEK_API_KEY:
        raise ValueError("ERROR: DeepSeek API key not found. Please set the DEEPSEEK_API_KEY environment variable in your .env file.")

    # PDF generation settings
    REPORT_TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'report_template.html')
