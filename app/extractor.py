from pydoc import text
import re

import os
import google.generativeai as genai

from pyparsing import line

SKILLS = [
    "Python",
    "Java",
    "C++",
    "SQL",
    "MySQL",
    "PostgreSQL",
    "React.js",
    "Node.js",
    "JavaScript",
    "HTML",
    "CSS",
    "Git",
    "GitHub",
    "FastAPI",
    "Flask",
    "Django",
    "Machine Learning",
    "Deep Learning",
    "TensorFlow",
    "PyTorch",
    "AWS",
    "Azure",
    "Docker"
]

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "models/gemini-3.8-flash"
)


def extract_email(text):

    emails = re.findall(
        r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
        text
    )

    return emails


def extract_phone(text):

    phones = re.findall(
        r'\+?\d[\d\s\-]{8,15}',
        text
    )

    return phones


def extract_skills(text):

    prompt = f"""
    Extract all skills from this resume.

    Include:

    - Technical Skills
    - Programming Languages
    - Frameworks
    - Databases
    - Cloud Platforms
    - Tools
    - Software
    - Methodologies
    - Business Skills
    - Management Skills
    - Marketing Skills
    - Soft Skills
    - Design Skills

    Return only comma separated skills.

    Resume:

    {text}
    """

    try:

        response = model.generate_content(
            prompt
        )

        skills_text = response.text.strip()

        skills = [
            skill.strip()
            for skill in skills_text.split(",")
            if skill.strip()
        ]

        return skills

    except Exception as e:

        print(
            "Skill Extraction Error:",
            e
        )

        return []

def extract_name(text):

    lines = text.split("\n")

    for line in lines[:10]:

        line = line.strip()

        if not line:
            continue

        # Skip emails
        if "@" in line:
            continue

        # Skip phone numbers
        if any(char.isdigit() for char in line):
            continue

        # Skip very long lines
        if len(line) > 40:
            continue

        words = line.split()

        if len(words) >= 2:
            return line

    return "Unknown Candidate"