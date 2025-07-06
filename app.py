from flask import Flask, request, render_template, redirect
import os
from werkzeug.utils import secure_filename
from resume_analysis import analyze_resume_relevance, full_resume_analysis
from job_seeking_agent import fetch_jobs_from_google, summarize_jobs_with_llm, extract_search_query, parse_job_text_to_list
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
        resume_analysis = analyze_resume_relevance(resume_text, user_input, llm)

        search_query = extract_search_query(user_input, llm)

        # if search_query == "TOO_VAGUE":
        #     job_summary = "⚠️ Your input was too vague. Please describe more clearly what kind of jobs you're looking for (skills, location, job type...)."
        #     jobs = []
        # else:
        #     jobs = fetch_jobs_from_google(search_query)
        #     job_summary = summarize_jobs_with_llm(jobs, llm)

        jobs = fetch_jobs_from_google(search_query)

        job_summary_text = summarize_jobs_with_llm(jobs, llm)
        job_structured_list = parse_job_text_to_list(job_summary_text)

        return render_template("results.html", resume_result=resume_analysis, job_list=job_structured_list)

        # job_summary = summarize_jobs_with_llm(jobs, llm)

        # return render_template("results.html", resume_result=resume_analysis, job_summary=job_summary)
    return render_template("index.html")

# @app.route("/chat", methods=["GET", "POST"])
# def chat():
#     if request.method == "POST":
#         message = request.form["message"]
#         response = llm.generate("User: " + message)
#         return render_template("chat.html", user_input=message, response=response)
#     return render_template("chat.html", user_input=None, response=None)

@app.route("/chat", methods=["GET", "POST"])
def chat():
    response = None
    resume_text = None

    if request.method == "POST":
        message = request.form.get("message")
        uploaded = request.files.get("resume")
        if uploaded:
            filename = secure_filename(uploaded.filename)
            path = os.path.join(UPLOAD_FOLDER, filename)
            uploaded.save(path)
            resume_text = extract_text_from_file(path)
            response = full_resume_analysis(resume_text, llm)
        elif message:
            response = llm.generate(f"You are a career chatbot.\nUser says: {message}")

    return render_template("chat.html", response=response)


if __name__ == "__main__":
    app.run(debug=True)