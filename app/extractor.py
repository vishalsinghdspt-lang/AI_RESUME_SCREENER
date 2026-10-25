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

    skill_database = [

    # Programming Languages
    "Python",
    "Java",
    "C",
    "C++",
    "C#",
    "JavaScript",
    "TypeScript",
    "Go",
    "Rust",
    "Kotlin",
    "Swift",
    "PHP",
    "Ruby",
    "Scala",
    "R",
    "MATLAB",

    # Frontend
    "HTML",
    "CSS",
    "Bootstrap",
    "Tailwind CSS",
    "SASS",
    "React",
    "Next.js",
    "Angular",
    "Vue.js",
    "Redux",
    "jQuery",

    # Backend
    "Node.js",
    "Express.js",
    "FastAPI",
    "Flask",
    "Django",
    "Spring Boot",
    "ASP.NET",
    "Laravel",

    # Databases
    "SQL",
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "SQLite",
    "Oracle",
    "Redis",
    "Firebase",
    "Supabase",
    "Cassandra",

    # Cloud
    "AWS",
    "Azure",
    "Google Cloud",
    "GCP",
    "Cloud Computing",
    "EC2",
    "S3",
    "Lambda",

    # DevOps
    "Docker",
    "Kubernetes",
    "Git",
    "GitHub",
    "GitLab",
    "CI/CD",
    "Jenkins",
    "Terraform",
    "Ansible",
    "Linux",
    "Bash",
    "Shell Scripting",

    # Data Science
    "Pandas",
    "NumPy",
    "Matplotlib",
    "Seaborn",
    "Plotly",
    "Data Analysis",
    "Data Visualization",
    "Statistics",
    "EDA",

    # Machine Learning
    "Machine Learning",
    "Deep Learning",
    "Supervised Learning",
    "Unsupervised Learning",
    "Regression",
    "Classification",
    "Clustering",
    "Feature Engineering",
    "Scikit-learn",

    # AI
    "Artificial Intelligence",
    "Generative AI",
    "Prompt Engineering",
    "LLM",
    "Large Language Models",
    "LangChain",
    "RAG",
    "Vector Database",
    "Embedding",
    "OpenAI",
    "Gemini",
    "Hugging Face",

    # NLP
    "Natural Language Processing",
    "NLP",
    "Text Mining",
    "Sentiment Analysis",
    "Transformers",
    "BERT",

    # Deep Learning Frameworks
    "TensorFlow",
    "Keras",
    "PyTorch",

    # Computer Vision
    "Computer Vision",
    "OpenCV",
    "YOLO",
    "Image Processing",
    "Object Detection",

    # Cybersecurity
    "Cyber Security",
    "Network Security",
    "Penetration Testing",
    "Ethical Hacking",
    "Kali Linux",
    "Burp Suite",
    "OWASP",
    "Cryptography",

    # Networking
    "Computer Networks",
    "TCP/IP",
    "DNS",
    "HTTP",
    "HTTPS",
    "Routing",
    "Switching",

    # Operating Systems
    "Operating Systems",
    "Linux",
    "Unix",
    "Windows Server",

    # Core CS Subjects
    "Data Structures",
    "Algorithms",
    "DBMS",
    "OOP",
    "Operating System",
    "Computer Networks",
    "System Design",

    # Mobile Development
    "Android",
    "Android Studio",
    "Flutter",
    "React Native",
    "Swift",
    "Kotlin",

    # Software Testing
    "Unit Testing",
    "Selenium",
    "Junit",
    "Pytest",
    "Postman",
    "API Testing",

    # Data Engineering
    "ETL",
    "Apache Spark",
    "Kafka",
    "Hadoop",
    "Data Warehouse",

    # Blockchain
    "Blockchain",
    "Ethereum",
    "Solidity",
    "Web3",

    # UI/UX
    "Figma",
    "Adobe XD",
    "UI Design",
    "UX Design",
    "Wireframing",
    "Prototyping",

    # Business Intelligence
    "Power BI",
    "Tableau",
    "Looker",

    # Tools
    "VS Code",
    "Jupyter Notebook",
    "PyCharm",
    "IntelliJ",
    "Eclipse",

    # Soft Skills
    "Leadership",
    "Communication",
    "Problem Solving",
    "Teamwork",
    "Critical Thinking",
    "Analytical Skills",
    "Project Management",
    "Time Management",

    # ATS / Resume Skills
    "Agile",
    "Scrum",
    "Kanban",
    "Product Management",
    "Software Development",
    "Software Engineering"
]

    found_skills = []

    text_lower = text.lower()

    for skill in skill_database:

        if skill.lower() in text_lower and skill not in found_skills:
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