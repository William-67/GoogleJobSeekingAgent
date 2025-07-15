from flask import Flask, request, render_template, redirect, session, url_for

import uuid
import json
import datetime

import os
from werkzeug.utils import secure_filename
from resume_analysis import analyze_resume_relevance
from job_seeking_agent import fetch_jobs_from_google, summarize_jobs_with_llm, extract_search_query, parse_job_text_to_list
from utils import extract_text_from_file, GeminiLLM
from config import Config
from chats import save_chat, list_all_saved_chats, load_chat, get_chat_path

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
llm = GeminiLLM()

# app.secret_key = Config.SECRET_KEY

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

        jobs = fetch_jobs_from_google(search_query)

        job_summary_text = summarize_jobs_with_llm(jobs, llm)
        job_structured_list = parse_job_text_to_list(job_summary_text)

        return render_template("results.html", resume_result=resume_analysis, job_list=job_structured_list)

        # job_summary = summarize_jobs_with_llm(jobs, llm)

        # return render_template("results.html", resume_result=resume_analysis, job_summary=job_summary)
    return render_template("index.html")

@app.route("/start-chat")
def start_chat():
    return render_template("start_chat.html")

@app.route("/chat/new", methods=["GET"])
def new_chat():
    chat_id = str(uuid.uuid4())
    new_chat_data = {
        "id": chat_id,
        "title": "Untitled Chat",
        "messages": [],
        "resume": "",
        "created_at": datetime.datetime.now().isoformat()
    }
    save_chat(chat_id, new_chat_data)
    return redirect(f"/chat/{chat_id}")

@app.route("/chat-history")
def chat_history():
    all_chats = list_all_saved_chats()
    return render_template("chat_history.html", chats=all_chats)

@app.route("/chat/<chat_id>/rename", methods=["POST"])
def rename_chat(chat_id):
    chat = load_chat(chat_id)
    new_title = request.form.get("new_title", "").strip()
    if new_title:
        chat["title"] = new_title
        save_chat(chat_id, chat)
    return redirect(url_for("chat", chat_id=chat_id))

@app.route("/chat/<chat_id>/delete", methods=["POST"])
def delete_chat(chat_id):
    path = get_chat_path(chat_id)
    if os.path.exists(path):
        os.remove(path)
    return redirect(url_for("chat_history"))


@app.route("/chat/<chat_id>", methods=["GET", "POST"])
def chat(chat_id):
    chat = load_chat(chat_id)
    response = None

    if request.method == "POST":
        # Upload resume only once
        if not chat.get("resume") and "resume" in request.files:
            file = request.files["resume"]
            if file and file.filename:
                filename = secure_filename(file.filename)
                path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(path)
                resume_text = extract_text_from_file(path)
                chat["resume"] = resume_text
                print("✅ Resume uploaded and extracted.")

        # User sending message
        message = request.form.get("message")
        if message:
            chat["messages"].append({"role": "user", "content": message})

            context = "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in chat["messages"])
            resume_text = chat.get("resume", "")
            resume_prompt = f"Here is the user's resume:\n{resume_text}\n\n" if resume_text else ""

            prompt = (
                "You are a career assistant AI.\n"
                + resume_prompt
                + f"Conversation so far:\n{context}\nAssistant:"
            )

            reply = llm.generate(prompt)
            chat["messages"].append({"role": "assistant", "content": reply})
            response = reply

        save_chat(chat_id, chat)

    return render_template("chat.html", chat=chat, response=response)


if __name__ == "__main__":
    app.run(debug=True)