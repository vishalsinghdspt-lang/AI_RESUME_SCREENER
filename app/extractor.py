from pydoc import text
import re

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

    found_skills = []

    for skill in SKILLS:

        if skill.lower() in text.lower():

            found_skills.append(skill)

    return found_skills

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