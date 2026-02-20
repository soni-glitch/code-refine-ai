from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import os
from fastapi.templating import Jinja2Templates

# Load environment variables
load_dotenv()

app = FastAPI()

# Setup templates folder
templates = Jinja2Templates(directory="templates")

# Setup Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Request structure
class CodeRequest(BaseModel):
    code: str
    language: str

# Prompt builder
def build_prompt(code, language):
    return f"""
You are a professional senior software engineer.

Analyze the following {language} code.

STRICT RULES:

1. If there are syntax or logical errors:
   - List all detected errors clearly.
   - Provide corrected full code.

2. If the code has NO errors:
   - Respond EXACTLY with:
   NO_ERRORS_FOUND

Code:
{code}
"""

# Home route
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Review API
@app.post("/review")
def review_code(request: CodeRequest):

    if not request.code.strip():
        return {"error": "Code cannot be empty"}

    prompt = build_prompt(request.code, request.language)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=2000
    )

    result = response.choices[0].message.content

    if "NO_ERRORS_FOUND" in result:
        return {
            "errors_found": False,
            "message": "No Errors Found ✅"
        }

    return {
        "errors_found": True,
        "analysis": result

    }
