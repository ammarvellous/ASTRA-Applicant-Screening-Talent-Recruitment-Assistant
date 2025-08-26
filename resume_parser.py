# resume_parser.py
import os
import json
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr, conint, ValidationError
from llm_loader import get_llm, get_watsonx_llm, get_gemini_llm
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import BaseOutputParser, OutputParserException
# import BaseOutputParser

load_dotenv()

# ------------------ Schema ------------------
class Project(BaseModel):
    name: str
    description: Optional[str]
    technologies: Optional[List[str]]

class CandidateData(BaseModel):
    name: str
    email: EmailStr
    phone: str
    location: Optional[str]
    years_experience: conint(ge=0, le=60)
    tech_stack: List[str]
    desired_positions: Optional[List[str]] = []
    projects: Optional[List[Project]] = []


# ------------------ Parser ------------------
class JSONOutputParser(BaseOutputParser):
    def parse(self, text: str) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise OutputParserException(f"Invalid JSON: {e}")


# ------------------ LLM Setup ------------------
def get_parser_llm(provider="watsonx"):
    """Get the appropriate LLM for resume parsing"""
    if provider == "watsonx":
        return get_watsonx_llm(model_id="ibm/granite-13b-instruct-v2")
    else:
        return get_gemini_llm(model_name="gemini-1.5-flash", temperature=0)


# ------------------ Prompt ------------------
parser = JSONOutputParser()

prompt = PromptTemplate(
    input_variables=["resume_text"],
    template=(
        "You are a resume parser. Extract structured information from the following text. "
        "Return valid JSON with the following schema:\n\n"
        "{{\n"
        '  "name": "Full Name",\n'
        '  "email": "email@example.com",\n'
        '  "phone": "+1234567890",\n'
        '  "location": "City, Country",\n'
        '  "years_experience": 5,\n'
        '  "tech_stack": ["Python","Django","Docker"],\n'
        '  "desired_positions": ["Backend Engineer"],\n'
        '  "projects": [\n'
        "      {{\n"
        '         "name": "Project Name",\n'
        '         "description": "Brief description of the project",\n'
        '         "technologies": ["Python","React"]\n'
        "      }}\n"
        "   ]\n"
        "}}\n\n"
        "Resume:\n{resume_text}\n\n"
        "Output ONLY the JSON."
    )
)


# ------------------ Chain ------------------
chain = prompt | get_parser_llm()

# chain = prompt | GeminiLLM(model_name="gemini-1.5-flash", temperature=0)

def parse_resume_to_json(resume_text: str) -> CandidateData:
    """
    Parse resume text into CandidateData via Watsonx + validation.
    """
    raw_output = chain.invoke({"resume_text": resume_text}).content

    # Extract the content string from the AIMessage
    if hasattr(raw_output, "content"):
        output_text = raw_output.content
    else:
        output_text = str(raw_output)

    import re
    json_match = re.search(r'(\{.*\})', output_text, re.DOTALL)
    if json_match:
        clean_json = json_match.group(1)
        try:
            data = json.loads(clean_json)
            return CandidateData(**data)
        except json.JSONDecodeError as e:
            print(f"Failed to parse extracted JSON: {e}")

    return CandidateData(**data)

# testing the function with sample
resume_text = """Mohammad Ammar/ 
Phone: +91 7365993869 | Email: mdammar1612@gmail.com|
LinkedIn: www.linkedin.com/in/mohammad-ammar369 | GitHub: https://github.com/ammarvellous
Education
St. Patrick’s Higher Secondary School, Asansol
ICSE | Percentile: 93.8%												2020
St. Patrick’s Higher Secondary School, Asansol
ISCE | Percentile: 88.2 %												2022
VIT Bhopal University
B. Tech - Computer Science and Engineering | CGPA: 9.1								2026
Technical Skills
Programming: Python, Java, C++, R, JavaScript, MySQL, Docker, CI/CD
Concepts: Data Structures & Algorithms (300+ LeetCode problems, 5-star HackerRank coder), Web Scraping, API Development, Cloud Computing
Tools & Frameworks: TensorFlow, OpenCV, Flask, FastAPI, MongoDB Atlas, Langflow, React, Node.js
Projects
Machine Learning
Sign Language Prediction											Oct’22
Engineered a CNN-based Sign Language Recognition model using the MNIST dataset, achieving 92%+ accuracy by leveraging convolution, pooling, and data augmentation techniques.
Early detection of ADHD disease										May’23
Developed an advanced deep learning framework integrating spatial and temporal fMRI scan data, reducing diagnostic time by 40% for clinical practitioners.
Application Development
Craft Connect													Dec’24
Developed a full-stack local services platform that connects users with professionals like electricians, plumbers, and carpenters.
Engineered a serverless backend utilizing Node.js, increasing API response rate by 60ms and enabling the application to handle 500 concurrent users with zero downtime..
Implemented an AI chatbot for instant user queries, geolocation-based service matching, and dynamic pricing algorithms for cost optimization.
Insight Scraper													Jan’22
Built a web-based intelligent scraper that integrates LLMs and web automation to extract and analyze structured data from any website.
Experience and Leadership
Core Member - AI Club											Apr’23 - Present
Spearheaded 3+ AI-driven projects and organized technical workshops attended by 100+ participants.
Data Science Club Champion 										Mar’22 - Mar’23
Secured 1st place in the club's data science quiz, earning exclusive club merchandise.
Intern - Indian Space Lab (2024-25)									Dec’24  Jan25
Developed a framework for automated quality control of satellite data, flagging over 1,000 anomalies per month and ensuring data integrity for downstream applications.
Achievements and Certifications
SIH 2022 Finalist - Advanced to Round 2 in India’s largest hackathon.
Hacktoberfest Contributor (Open Source) - Successfully contributed to 10+ repositories in global open-source initiatives.
Certifications:
Cloud Computing - IIT Kharagpur (Top 2% - Silver Elite, 2024)
Disaster Risk Monitoring Using Satellite Imagery - NVIDIA (2024)
The Bits and Bytes of Computer Networking - Google (2023)
Additional 
Languages: English, Hindi, Urdu, Bengali
Soft Skills: Rapid learning, problem-solving, adaptability, effective communication
"""


if __name__ == "__main__":
#     # Simple LLM sanity check
    print(parse_resume_to_json(resume_text))