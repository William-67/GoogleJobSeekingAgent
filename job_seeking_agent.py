import requests
import os
from config import Config

SERPAPI_KEY = Config.SERPAPI_KEY
def fetch_jobs_from_google(query):
    params = {
        "engine": "google_jobs",
        "q": query,
        "hl": "en",
        "api_key": SERPAPI_KEY
    }
    res = requests.get("https://serpapi.com/search", params=params)
    return res.json().get("jobs_results", [])

def summarize_jobs_with_llm(job_results, llm):
    summary_prompt = "Summarize the following job results clearly with job title, company, location, and a short summary. Include links.\n\n"
    for job in job_results:
        summary_prompt += f"- {job.get('title')} at {job.get('company_name')} in {job.get('location')}\nDescription: {job.get('description')}\nLink: {job.get('job_apply_link')}\n\n"
    return llm.generate(summary_prompt)