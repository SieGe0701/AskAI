# Main Flask app
import os
from flask import Flask, request, render_template, jsonify
from langchain_openai import ChatOpenAI
import google.generativeai as genai
from dotenv import load_dotenv
from PyPDF2 import PdfReader  # Import for reading PDF files
import mimetypes

load_dotenv()
api_key = os.getenv('api_key')

app = Flask(__name__)

genai.configure(api_key=api_key)

# Upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_file():
    file = request.files['file']
    question = request.form.get('question')

    if not file or not question:
        return render_template('process.html')

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Determine if the file is a PDF
    mime_type, _ = mimetypes.guess_type(file_path)
    state = None

    if mime_type == 'application/pdf':  # If the file is a PDF
        try:
            reader = PdfReader(file_path)
            file_content = ""
            for page in reader.pages:
                file_content += page.extract_text()
            state = file_content
        except Exception as e:
            return jsonify({"error": f"Failed to read the PDF file: {e}"}), 500
    else:  # If the file is a text file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                state = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                state = f.read()
        except Exception as e:
            return jsonify({"error": f"Failed to read the file: {e}"}), 500

    # Use Generative Model to generate a response
    model = genai.GenerativeModel("gemini-1.5-flash")
    try:
        response = model.generate_content(f"For the content of a data given below\n{state}\nAnswer the question below. If there are multiple records, separate them with a newline\n{question}")
        answer = response.text
    except Exception as e:
        return jsonify({"error": f"Failed to generate a response: {e}"}), 500

    return render_template("process.html", question=question, answer=answer)

if __name__ == '__main__':
    app.run(debug=True)
