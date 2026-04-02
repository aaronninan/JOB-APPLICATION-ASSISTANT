import os
from typing import Dict, List

from flask import Flask, jsonify, render_template, request

import google.generativeai as genai


app = Flask(__name__)


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Warning: GEMINI_API_KEY is not set. API calls will fail until you add it.")



MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


def build_agent_prompt(resume_text: str, job_description: str) -> str:
    """Build the exact agent-style prompt required by the assignment."""
    return f"""You are an AI Job Application Assistant Agent.

Follow these steps:

Step 1: Analyze the resume carefully
Step 2: Analyze the job description
Step 3: Identify missing skills
Step 4: Identify weak areas
Step 5: Suggest improvements

Think step-by-step before answering.

Return output in this format:

Missing Skills:

* ...

Weak Areas:

* ...

Suggestions:

* ...

Resume:
{resume_text}

Job Description:
{job_description}
"""


def parse_bullet_sections(raw_text: str) -> Dict[str, List[str]]:
    """
    Convert the model text into structured JSON lists for the frontend.
    Expected sections:
    - Missing Skills
    - Weak Areas
    - Suggestions
    """
    sections = {
        "missing_skills": [],
        "weak_areas": [],
        "suggestions": [],
    }

    current_section = None
    section_map = {
        "missing skills:": "missing_skills",
        "weak areas:": "weak_areas",
        "suggestions:": "suggestions",
    }

    for line in raw_text.splitlines():
        clean_line = line.strip()
        lower_line = clean_line.lower()

        if lower_line in section_map:
            current_section = section_map[lower_line]
            continue

        if clean_line.startswith("*") or clean_line.startswith("-"):
            item = clean_line[1:].strip()
            if current_section and item:
                sections[current_section].append(item)

    return sections


@app.route("/")
def index():
    """Serve the main page."""
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """Analyze resume + job description using Gemini and return JSON."""
    try:
        data = request.get_json(silent=True) or {}
        resume_text = data.get("resume", "").strip()
        job_description = data.get("job_description", "").strip()

        print("\n--- User Input Received ---")
        print("Resume:\n", resume_text)
        print("Job Description:\n", job_description)

        if not resume_text or not job_description:
            return jsonify({"error": "Please provide both resume and job description."}), 400

        if not GEMINI_API_KEY:
            return jsonify(
                {
                    "error": "Missing GEMINI_API_KEY. Set it before running the app."
                }
            ), 500

        prompt = build_agent_prompt(resume_text, job_description)

        print("\n--- Agent Processing Started ---")
        print("Using model:", MODEL_NAME)
        print("Prompt prepared successfully.")

        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        response_text = (response.text or "").strip()

        print("\n--- Gemini API Response ---")
        print(response_text)

        parsed_response = parse_bullet_sections(response_text)

        return jsonify(
            {
                "raw_response": response_text,
                "missing_skills": parsed_response["missing_skills"],
                "weak_areas": parsed_response["weak_areas"],
                "suggestions": parsed_response["suggestions"],
            }
        )
    except Exception as error:
        print("\n--- Error During Analysis ---")
        print(str(error))
        return jsonify({"error": str(error)}), 500


if __name__ == "__main__":
    app.run(debug=True)
