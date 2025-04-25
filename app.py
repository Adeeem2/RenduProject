from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import os
from werkzeug.utils import secure_filename
import uuid

# Import our custom modules
from config import Config
from report_generator import generate_report

app = Flask(__name__)
app.config.from_object(Config)

# Ensure the secret key is set
if not app.secret_key:
    app.secret_key = Config.SECRET_KEY

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """Render the main page with file upload form."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads and initiate report generation."""
    if 'instruction_file' not in request.files or 'code_files' not in request.files:
        flash('Fichiers requis manquants', 'warning')
        return redirect(request.url)

    instruction_file = request.files['instruction_file']
    code_files = request.files.getlist('code_files')

    if instruction_file.filename == '' or not code_files or code_files[0].filename == '':
        flash('Aucun fichier sélectionné', 'warning')
        return redirect(request.url)

    # Create a unique session ID for this report
    session_id = str(uuid.uuid4())
    session_folder = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(session_folder, exist_ok=True)

    # Save instruction file
    instruction_filename = secure_filename(instruction_file.filename)
    instruction_path = os.path.join(session_folder, instruction_filename)
    instruction_file.save(instruction_path)

    # Save code files
    code_paths = []
    for code_file in code_files:
        if code_file and code_file.filename != '':
            code_filename = secure_filename(code_file.filename)
            code_path = os.path.join(session_folder, code_filename)
            code_file.save(code_path)
            code_paths.append(code_path)

    # Generate the report
    try:
        report_path = generate_report(instruction_path, code_paths, session_folder)
        return redirect(url_for('download_report', session_id=session_id, filename=os.path.basename(report_path)))
    except Exception as e:
        flash(f'Erreur lors de la génération du rapport: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/download/<session_id>/<filename>')
def download_report(session_id, filename):
    """Serve the generated report for download."""
    report_path = os.path.join(app.config['UPLOAD_FOLDER'], session_id, filename)
    return send_file(report_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
