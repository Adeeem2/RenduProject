import os
import io
import tempfile
import subprocess
from pathlib import Path
import base64
import json
import matplotlib.pyplot as plt
from PIL import Image
import requests
import markdown
import pdfkit
import re

from config import Config

# Configure DeepSeek API
DEEPSEEK_API_KEY = Config.DEEPSEEK_API_KEY
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def extract_text_from_file(file_path):
    """Extract text from a file using DeepSeek API."""
    try:
        # For PDF and image files, we'll use the DeepSeek API to extract text
        # First, encode the file as base64
        with open(file_path, 'rb') as f:
            file_content = f.read()
            file_base64 = base64.b64encode(file_content).decode('utf-8')

        # Use DeepSeek API to extract text
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek-vision",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that extracts text from images and documents."},
                {"role": "user", "content": [
                    {"type": "text", "text": "Extract all the text from this document."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{file_base64}"}}
                ]}
            ]
        }

        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()

        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error extracting text from file: {str(e)}")
        return ""

def parse_instruction_file(file_path):
    """Parse the instruction file to extract title and objectives."""
    file_ext = Path(file_path).suffix.lower()

    if file_ext in ['.pdf', '.png', '.jpg', '.jpeg']:
        text = extract_text_from_file(file_path)
    elif file_ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        raise ValueError(f"Unsupported instruction file format: {file_ext}")

    # Use DeepSeek API to extract title and objectives
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that extracts information from lab instructions."},
            {"role": "user", "content": f"Extract the lab title, objectives, and exercise titles from the following text. Format your response as JSON with keys 'title', 'objectives' (as a list), and 'exercises' (as a list of exercise titles):\n\n{text}"}
        ]
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors

        response_data = response.json()
        result = json.loads(response_data["choices"][0]["message"]["content"])
        return result
    except Exception as e:
        print(f"Error using DeepSeek API: {str(e)}")
        # Fallback to a simple structure
        return {
            "title": "Lab Report",
            "objectives": ["Analyze and document code functionality"],
            "exercises": ["Code Analysis"]
        }

def read_code_file(file_path):
    """Read a code file and return its content."""
    file_ext = Path(file_path).suffix.lower()

    if file_ext == '.ipynb':
        return read_jupyter_notebook(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

def read_jupyter_notebook(file_path):
    """Read a Jupyter Notebook file and extract code cells."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                notebook = json.load(f)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid Jupyter notebook format: {file_path} is not a valid JSON file")

        if 'cells' not in notebook:
            raise ValueError(f"Invalid Jupyter notebook structure: 'cells' not found in {file_path}")

        code_content = ""
        for cell in notebook.get('cells', []):
            if cell.get('cell_type') == 'code':
                source = cell.get('source', [])
                if isinstance(source, list):
                    code_content += ''.join(source) + "\n\n"
                else:
                    code_content += source + "\n\n"

        return code_content
    except Exception as e:
        # Re-raise with a more descriptive message
        raise ValueError(f"Error processing Jupyter notebook: {str(e)}")

def analyze_code(code, language, exercise_title=None):
    """Use DeepSeek API to analyze and explain the code.

    If exercise_title is provided, extract and analyze only the relevant code block for that exercise.
    """
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    # If exercise_title is provided, ask DeepSeek to extract the relevant code block
    if exercise_title:
        # First, extract the relevant code block for this exercise
        extract_payload = {
            "model": "deepseek-coder",
            "messages": [
                {"role": "system", "content": "You are a helpful programming assistant."},
                {"role": "user", "content": f"Extract the code block that corresponds to '{exercise_title}' from the following {language} code. Return ONLY the extracted code, nothing else. If you can't identify a specific block, return a representative portion of the code that would be most relevant to this exercise:\n\n```{language}\n{code}\n```"}
            ]
        }

        try:
            extract_response = requests.post(DEEPSEEK_API_URL, headers=headers, json=extract_payload)
            extract_response.raise_for_status()

            extract_data = extract_response.json()
            extracted_code = extract_data["choices"][0]["message"]["content"]

            # Clean up the extracted code (remove markdown code block markers if present)
            extracted_code = re.sub(r'^```.*\n', '', extracted_code)
            extracted_code = re.sub(r'\n```$', '', extracted_code)

            # Use the extracted code for analysis
            code_to_analyze = extracted_code
        except Exception as e:
            print(f"Error extracting code block: {str(e)}")
            code_to_analyze = code  # Fallback to the full code
    else:
        code_to_analyze = code

    # Now analyze the code
    analysis_payload = {
        "model": "deepseek-coder",
        "messages": [
            {"role": "system", "content": "You are a helpful programming assistant."},
            {"role": "user", "content": f"Analyze the following {language} code and provide a detailed explanation of what it does, its structure, and any notable algorithms or techniques used:\n\n```{language}\n{code_to_analyze}\n```"}
        ]
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=analysis_payload)
        response.raise_for_status()

        response_data = response.json()
        return {
            "code_block": code_to_analyze,
            "explanation": response_data["choices"][0]["message"]["content"]
        }
    except Exception as e:
        print(f"Error using DeepSeek API: {str(e)}")
        return {
            "code_block": code_to_analyze,
            "explanation": f"Error analyzing code: {str(e)}"
        }

def interpret_plot(plot_path):
    """Use DeepSeek API to provide a scientific interpretation of a plot."""
    try:
        # Encode the plot image as base64
        with open(plot_path, 'rb') as f:
            plot_content = f.read()
            plot_base64 = base64.b64encode(plot_content).decode('utf-8')

        # Use DeepSeek API to interpret the plot
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek-vision",
            "messages": [
                {"role": "system", "content": "You are a scientific data analyst specializing in interpreting plots and visualizations."},
                {"role": "user", "content": [
                    {"type": "text", "text": "Provide a detailed scientific interpretation of this plot. Describe what it shows, the trends or patterns visible, and what scientific conclusions might be drawn from it. Be specific and technical in your analysis."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{plot_base64}"}}
                ]}
            ]
        }

        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()

        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error interpreting plot: {str(e)}")
        return "Unable to provide plot interpretation."

def execute_python_code(code_path, output_dir):
    """Execute Python code in a safe environment and capture output and plots."""
    results = {
        "output": "",
        "plots": [],
        "plot_interpretations": {},
        "error": None
    }

    # Create a temporary directory for execution
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy the code file to the temp directory
        file_ext = Path(code_path).suffix.lower()

        if file_ext == '.ipynb':
            # For Jupyter notebooks, extract code and save as a Python file
            code_content = read_jupyter_notebook(code_path)
            temp_code_path = os.path.join(temp_dir, os.path.basename(code_path).replace('.ipynb', '.py'))
            with open(temp_code_path, 'w', encoding='utf-8') as dst:
                dst.write(code_content)
        else:
            # For regular Python files
            temp_code_path = os.path.join(temp_dir, os.path.basename(code_path))
            with open(code_path, 'r', encoding='utf-8') as src, open(temp_code_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())

        # Execute the code and capture output
        try:
            # Add matplotlib code to save figures
            plot_capture_code = """
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Store the original plt.figure and plt.savefig functions
original_figure = plt.figure
original_show = plt.show

# Counter for figure files
figure_counter = 0

# Override plt.figure to track created figures
def custom_figure(*args, **kwargs):
    global figure_counter
    fig = original_figure(*args, **kwargs)
    figure_counter += 1
    return fig

# Override plt.show to save figures instead of displaying them
def custom_show():
    global figure_counter
    plt.savefig(f'figure_{figure_counter}.png')
    original_show()

plt.figure = custom_figure
plt.show = custom_show
"""

            # Create a wrapper script that captures matplotlib plots
            wrapper_path = os.path.join(temp_dir, "wrapper.py")
            with open(wrapper_path, 'w', encoding='utf-8') as f:
                f.write(plot_capture_code)
                f.write(f"\n\n# Execute the original script\nexec(open('{os.path.basename(temp_code_path)}').read())\n")

            # Run the wrapper script
            process = subprocess.run(
                ['python', wrapper_path],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=30  # Limit execution time to 30 seconds
            )

            results["output"] = process.stdout
            if process.stderr:
                results["error"] = process.stderr

            # Collect any generated plot images and interpret them
            for file in os.listdir(temp_dir):
                if file.startswith("figure_") and file.endswith(".png"):
                    plot_path = os.path.join(temp_dir, file)
                    output_plot_path = os.path.join(output_dir, file)
                    with open(plot_path, 'rb') as src, open(output_plot_path, 'wb') as dst:
                        dst.write(src.read())
                    results["plots"].append(output_plot_path)

                    # Interpret the plot
                    interpretation = interpret_plot(output_plot_path)
                    results["plot_interpretations"][file] = interpretation

        except subprocess.TimeoutExpired:
            results["error"] = "Code execution timed out (limit: 30 seconds)"
        except Exception as e:
            results["error"] = str(e)

    return results

def generate_markdown_content(lab_info, code_analyses):
    """Generate Markdown content for the lab report."""
    md_content = []

    # Title
    md_content.append(f"# {lab_info.get('title', 'Lab Report')}\n")

    # Objectives
    md_content.append("## Objectives\n")
    for objective in lab_info.get("objectives", []):
        md_content.append(f"* {objective}\n")
    md_content.append("\n")

    # Code analyses
    for i, analysis in enumerate(code_analyses):
        # Exercise title if available
        if i < len(lab_info.get("exercises", [])):
            exercise_title = lab_info["exercises"][i]
            md_content.append(f"## Exercise: {exercise_title}\n")
        else:
            md_content.append(f"## Code Sample {i+1}\n")

        # File name
        md_content.append(f"**File:** {analysis['filename']}\n\n")

        # Code block
        md_content.append("### Source Code\n")
        md_content.append(f"```{analysis['language']}\n{analysis.get('code_block', analysis['code'][:1000] + ('...' if len(analysis['code']) > 1000 else ''))}\n```\n\n")

        # Analysis
        md_content.append("### Analysis\n")
        md_content.append(f"{analysis['explanation']}\n\n")

        # Output (for Python files)
        if analysis.get('execution_results'):
            if analysis['execution_results'].get('output'):
                md_content.append("### Execution Output\n")
                md_content.append(f"```\n{analysis['execution_results']['output'][:500] + ('...' if len(analysis['execution_results']['output']) > 500 else '')}\n```\n\n")

            if analysis['execution_results'].get('error'):
                md_content.append("### Execution Error\n")
                md_content.append(f"```\n{analysis['execution_results']['error']}\n```\n\n")

            # Add plots if any
            for plot_path in analysis['execution_results'].get('plots', []):
                plot_filename = os.path.basename(plot_path)
                md_content.append("### Generated Plot\n")
                md_content.append(f"![{plot_filename}]({plot_path})\n\n")

                # Add plot interpretation if available
                if analysis['execution_results'].get('plot_interpretations') and plot_filename in analysis['execution_results']['plot_interpretations']:
                    md_content.append("#### Plot Interpretation\n")
                    md_content.append(f"{analysis['execution_results']['plot_interpretations'][plot_filename]}\n\n")

    return "".join(md_content)

def generate_pdf_report(lab_info, code_analyses, output_dir):
    """Generate a PDF report with the lab information and code analyses using Markdown."""
    # Generate Markdown content
    md_content = generate_markdown_content(lab_info, code_analyses)

    # Save Markdown content to a file
    md_path = os.path.join(output_dir, "lab_report.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    # Convert Markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])

    # Add some basic styling
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            h1 {{ color: #333; }}
            h2 {{ color: #444; margin-top: 20px; }}
            h3 {{ color: #555; }}
            pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }}
            code {{ font-family: Consolas, monospace; }}
            img {{ max-width: 100%; height: auto; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Save HTML content to a file
    html_path = os.path.join(output_dir, "lab_report.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(styled_html)

    # Convert HTML to PDF
    pdf_path = os.path.join(output_dir, "lab_report.pdf")
    try:
        pdfkit.from_file(html_path, pdf_path)
    except Exception as e:
        print(f"Error converting HTML to PDF: {str(e)}")
        # If pdfkit fails, try to use the HTML file directly
        return html_path

    return pdf_path

def generate_report(instruction_path, code_paths, output_dir):
    """Main function to generate a lab report from instruction and code files."""
    # Parse the instruction file
    lab_info = parse_instruction_file(instruction_path)

    # Analyze each code file
    code_analyses = []
    for i, code_path in enumerate(code_paths):
        file_ext = Path(code_path).suffix.lower()
        language = {'.py': 'python', '.java': 'java', '.c': 'c', '.ipynb': 'python'}.get(file_ext, 'text')

        code = read_code_file(code_path)

        # Get the exercise title if available
        exercise_title = None
        if i < len(lab_info.get("exercises", [])):
            exercise_title = lab_info["exercises"][i]

        # Analyze the code with the exercise title to extract the relevant block
        analysis_result = analyze_code(code, language, exercise_title)

        analysis = {
            'filename': os.path.basename(code_path),
            'language': language,
            'code': code,
            'code_block': analysis_result['code_block'],
            'explanation': analysis_result['explanation']
        }

        # Execute Python code if applicable
        if language == 'python' or file_ext == '.ipynb':
            execution_results = execute_python_code(code_path, output_dir)
            analysis['execution_results'] = execution_results

        code_analyses.append(analysis)

    # Generate the PDF report
    report_path = generate_pdf_report(lab_info, code_analyses, output_dir)
    return report_path
