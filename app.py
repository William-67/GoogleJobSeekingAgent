from flask import Flask, request, render_template, redirect
import os
from werkzeug.utils import secure_filename
from resume_analysis import analyze_resume_with_llm
from job_seeking_agent import fetch_jobs_from_google, summarize_jobs_with_llm
from utils import extract_text_from_file, GeminiLLM

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
llm = GeminiLLM()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["resume"]
        user_input = request.form["requirements"]
        path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(path)
        resume_text = extract_text_from_file(path)
        resume_analysis = analyze_resume_with_llm(resume_text, user_input, llm)
        jobs = fetch_jobs_from_google(user_input)
        job_summary = summarize_jobs_with_llm(jobs, llm)
        return render_template("results.html", resume_result=resume_analysis, job_summary=job_summary)
    return render_template("index.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        message = request.form["message"]
        response = llm.generate("User: " + message)
        return render_template("chat.html", user_input=message, response=response)
    return render_template("chat.html", user_input=None, response=None)

if __name__ == "__main__":
    app.run(debug=True)