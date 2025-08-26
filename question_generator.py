from typing import List
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from resume_parser import CandidateData
import os

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

def generate_tech_questions(candidate: CandidateData) -> List[str]:
    techs = ", ".join(candidate.tech_stack)
    prompt = PromptTemplate(
        input_variables=["techs"],
        template="""
        You are an interviewer. Generate 3-5 concise technical interview questions
        for a candidate skilled in {techs}. Questions should test depth of knowledge,
        not trivia. Return only a numbered list.
        """
    )
    response = llm.invoke(prompt.format(techs=techs))
    return response.content.split("\n")

def generate_project_questions(candidate: CandidateData) -> List[str]:
    questions = []
    for project in candidate.projects:
        q = f"Can you explain more about your project '{project['name']}'? What was your role and what challenges did you face?"
        questions.append(q)
    return questions

def generate_job_specific_questions(job_desc: str) -> List[str]:
    prompt = f"""
    Based on this job description:
    {job_desc}
    
    Generate 3-5 interview questions to evaluate a candidate's suitability.
    Return only a numbered list.
    """
    response = llm.invoke(prompt)
    return response.content.split("\n")
