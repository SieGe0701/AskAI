# Main Flask app
import os
from flask import Flask, request, render_template, jsonify
from langchain_openai import ChatOpenAI
import google.generativeai as genai
from dotenv import load_dotenv
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

    
    with open(file_path, 'r') as f:
        file_content = f.read()
        state = file_content

   
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"For the content of a data given below\n{state}\nAnswer the question below. If there are multiple records, separate them with a newline\n{question}")


    
    answer = response.text

    
    return render_template("process.html",question=question,answer=answer)

if __name__ == '__main__':
    app.run(debug=True)
