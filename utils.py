import fitz
import google.generativeai as genai
import os
from config import Config

# Initialize Gemini Model
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def extract_text_from_file(file_path):
    if file_path.endswith(".pdf"):
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text.lower()
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().lower()

class GeminiLLM:
    def generate(self, prompt):
        response = model.generate_content(prompt)
        return response.text
