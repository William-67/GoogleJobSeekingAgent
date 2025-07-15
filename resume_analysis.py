def analyze_resume_relevance(resume_text, user_prompt, llm):
    prompt = f"""You are a career assistant AI.

The user has uploaded their resume and wants to search jobs with this query:

"{user_prompt}"

Here is their resume:
{resume_text}

Please:
- Briefly list 3-5 points about how well the resume matches this job query, each as a clear bullet point.
- List any obvious gaps as bullet points, each point separated by a blank line.
- Use * or - as bullet points, and add a blank line between every bullet.
- DO NOT write long paragraphs.

Example output:

* Strength: Has direct experience with Python programming.

* Gap: Lacks Canadian work experience.

* Recommendation: Add more teamwork examples.
"""
    return llm.generate(prompt)


# def full_resume_analysis(resume_text, llm):
#     prompt = f"""You are a resume review AI assistant.

# Here is a user's full resume:
# {resume_text}

# Please analyze it and give structured suggestions to improve format, content, keyword relevance, and clarity.
# Include sections for:
# - Strengths
# - Weaknesses
# - Recommendations

# - List any obvious gaps as bullet points, each point separated by a blank line.
# - Use * or - as bullet points, and add a blank line between every bullet.
# - DO NOT write long paragraphs.

# Example output:

# * Strength: Has direct experience with Python programming.

# * Gap: Lacks Canadian work experience.

# * Recommendation: Add more teamwork examples.

# """
#     return llm.generate(prompt)

