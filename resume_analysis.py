def analyze_resume_relevance(resume_text, user_prompt, llm):
    prompt = f"""You're a career assistant AI. A user has uploaded their resume and written the following request:

{user_prompt}

Below is the content of their resume:
{resume_text}

Please analyze their resume and offer personalized suggestions on improvements, missing skills, or how well it fits their job goals. Format your response clearly.
Please assess how well the resume matches this job query.
- Highlight relevant skills or experience.
- Mention gaps or improvements needed.
- Keep it concise (use bullet points).

"""
    return llm.generate(prompt)

def full_resume_analysis(resume_text, llm):
    prompt = f"""You are a resume review AI assistant.

Here is a user's full resume:
{resume_text}

Please analyze it and give structured suggestions to improve format, content, keyword relevance, and clarity.
Include sections for:
- Strengths
- Weaknesses
- Recommendations
"""
    return llm.generate(prompt)
