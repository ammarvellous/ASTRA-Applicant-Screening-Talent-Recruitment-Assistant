from typing import List, Dict, Any
import random
from llm_loader import get_llm

llm = get_llm("gemini")

def generate_tech_questions(candidate: Dict[str, Any]) -> List[str]:
    """Generate questions about the candidate's technical skills"""
    # Get the candidate's tech stack
    tech_stack = ", ".join(candidate["tech_stack"]) if "tech_stack" in candidate and candidate["tech_stack"] else ""
    
    # If tech stack is empty, return a generic tech question
    if not tech_stack:
        return ["Tell me about your technical skills and proficiencies."]
    
    # Randomly select up to 2 technologies
    selected_techs = random.sample(candidate["tech_stack"], min(2, len(candidate["tech_stack"])))
    
    # Generate questions about these technologies
    prompt = f"""
    Generate 2 technical interview questions about the following technologies: {', '.join(selected_techs)}.
    The questions should be specific and test deep understanding of these technologies.
    Return only a numbered list of questions.
    """
    
    response = llm.invoke(prompt)
    # Extract questions from the response
    questions = [line.strip() for line in response.content.split("\n") 
                if line.strip() and not line.strip().isdigit() and len(line) > 10]
    return questions[:2]  # Return maximum 2 questions

def generate_project_questions(candidate: Dict[str, Any]) -> List[str]:
    """Generate questions about the candidate's projects"""
    # Get the candidate's projects
    projects = candidate["projects"] if "projects" in candidate else []
    
    # If no projects, return a generic project question
    if not projects:
        return ["Tell me about a significant project you've worked on."]
    
    # Randomly select up to 2 projects
    selected_projects = random.sample(projects, min(2, len(projects)))
    
    # Build prompt with project details
    project_details = []
    for project in selected_projects:
        name = project.get("name", "Unnamed project")
        description = project.get("description", "No description provided")
        technologies = project.get("technologies", [])
        tech_str = ", ".join(technologies) if technologies else "unspecified technologies"
        
        project_details.append(f"Project: {name}\nDescription: {description}\nTechnologies: {tech_str}")
    
    prompt = f"""
    Generate specific interview questions about these projects:
    
    {"\n\n".join(project_details)}
    
    The questions should probe the candidate's role, challenges faced, and technical decisions made.
    Return only a numbered list of questions, one question per project.
    """
    
    response = llm.invoke(prompt)
    # Extract questions from the response
    questions = [line.strip() for line in response.content.split("\n") 
                if line.strip() and not line.strip().isdigit() and len(line) > 10]
    return questions[:2]  # Return maximum 2 questions

def generate_job_questions(job_role: str) -> List[str]:
    """Generate job-specific questions"""
    prompt = f"""
    Generate 2 interview questions for a {job_role} position.
    These should be general professional questions not related to specific technologies.
    Return only a numbered list of questions.
    """
    response = llm.invoke(prompt)
    # Extract questions from the response
    questions = [line.strip() for line in response.content.split("\n") 
                if line.strip() and not line.strip().isdigit() and len(line) > 10]
    return questions[:2]  # Return maximum 2 questions