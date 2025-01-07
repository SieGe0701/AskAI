import os
from flask import Flask, request, render_template, jsonify
from langchain_openai import ChatOpenAI
import google.generativeai as genai
from dotenv import load_dotenv
from PyPDF2 import PdfReader  # Import for reading PDF files
from io import BytesIO
import mimetypes

load_dotenv()
api_key = os.getenv('api_key')

app = Flask(__name__)

genai.configure(api_key=api_key)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_file():
    file = request.files['file']
    question = request.form.get('question')

    if not file or not question:
        return render_template('process.html')

    try:
        file_content = ""
        mime_type, _ = mimetypes.guess_type(file.filename)

        if mime_type == 'application/pdf':  # If the file is a PDF
            reader = PdfReader(BytesIO(file.read()))
            for page in reader.pages:
                file_content += page.extract_text()
        else:  # If the file is a text file
            file_content = file.read().decode('utf-8')
    except Exception as e:
        return jsonify({"error": f"Failed to process the file: {e}"}), 500

    # Use Generative Model to generate a response
    model = genai.GenerativeModel("gemini-1.5-flash")
    try:
        response = model.generate_content(
            f"For the content of a data given below\n{file_content}\nAnswer the question below. If there are multiple records, separate them with a newline\n{question}"
        )
        answer = response.text
    except Exception as e:
        return jsonify({"error": f"Failed to generate a response: {e}"}), 500

    return render_template("process.html", question=question, answer=answer)

if __name__ == '__main__':
    app.run(debug=True)
