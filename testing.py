import google.generativeai as genai
import os

# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
genai.configure(api_key="apikey")

for model in genai.list_models():
    print(f"{model.name} - {model.supported_generation_methods}")
