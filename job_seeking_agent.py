import requests
from config import Config

def fetch_jobs_from_google(query):
    params = {
        "engine": "google_jobs",
        "q": query,
        "hl": "en",
        "api_key": Config.SERPAPI_KEY
    }
    res = requests.get("https://serpapi.com/search", params=params)
    return res.json().get("jobs_results", [])

def extract_search_query(user_input, llm):
    prompt = f"""You are a job assistant AI. A user wrote this job search request:

\"\"\"{user_input}\"\"\"

Your task is to convert this into a short, precise Google Jobs search query (around 5-10 keywords).
Focus on job title, level, skill, and location. Do not explain. Just return the query.
If the request is unclear or too vague to search, return "TOO_VAGUE".
"""
    
    return llm.generate(prompt).strip()


# def summarize_jobs_with_llm(job_results, llm):
#     if not job_results:
#         return "❗ No job results found."

#     prompt = "Please summarize the following job postings. For each job, provide:\n" \
#              "- Job Title\n- Company\n- Location\n- A short summary of the description\n- Link to apply\n\n"

#     for job in job_results:
#         prompt += "---\n"
#         prompt += f"Title: {job.get('title')}\n"
#         prompt += f"Company: {job.get('company_name')}\n"
#         prompt += f"Location: {job.get('location')}\n"
#         prompt += f"Description: {job.get('description', '')[:500]}\n"
#         prompt += f"Link: {job.get('job_apply_link') or job.get('detected_extensions', {}).get('link', 'N/A')}\n"

#     return llm.generate(prompt)



def summarize_jobs_with_llm(job_results, llm):
    if not job_results:
        return "❗ No job results found."

    prompt = "You are a job assistant AI. For each job below, return:" \
             "Title: <job title>\nCompany: <company name>\nLocation: <location>\nSummary: <one-line summary>\nLink: <link>\n\n"

    for job in job_results[:5]:
        desc = job.get("description", "")
        desc_clean = desc.replace("\n", " ").replace("\r", " ").strip()
        desc_short = desc_clean[:300]

        prompt += f"---\n"
        prompt += f"Title: {job.get('title')}\n"
        prompt += f"Company: {job.get('company_name')}\n"
        prompt += f"Location: {job.get('location')}\n"
        prompt += f"Description: {desc_short}\n"
        prompt += f"Link: {job.get('job_apply_link') or job.get('detected_extensions', {}).get('link', 'N/A')}\n"

    return llm.generate(prompt)

def parse_job_text_to_list(text):
    jobs = []
    entries = text.strip().split("Title:")
    for entry in entries[1:]:
        fields = {"title": "", "company": "", "location": "", "summary": "", "link": ""}
        lines = entry.strip().split("\n")
        fields["title"] = lines[0].strip()
        for line in lines[1:]:
            if line.startswith("Company:"):
                fields["company"] = line.replace("Company:", "").strip()
            elif line.startswith("Location:"):
                fields["location"] = line.replace("Location:", "").strip()
            elif line.startswith("Summary:"):
                fields["summary"] = line.replace("Summary:", "").strip()
            elif line.startswith("Link:"):
                fields["link"] = line.replace("Link:", "").strip()
        jobs.append(fields)
    return jobs