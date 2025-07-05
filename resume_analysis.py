def analyze_resume_with_llm(resume_text, user_prompt, llm):
    prompt = f"""You're a career assistant AI. A user has uploaded their resume and written the following request:

{user_prompt}

Below is the content of their resume:
{resume_text}

Please analyze their resume and offer personalized suggestions on improvements, missing skills, or how well it fits their job goals. Format your response clearly.
"""
    return llm.generate(prompt)