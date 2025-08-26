# db_utils.py
from pymongo import MongoClient
import os
import re
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

mongo_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongo_uri)
db = client["Astra"]
candidates_col = db["candidates"]
responses_col = db["responses"]
evaluated_responses_col = db["evaluated_responses"]

def save_candidate(candidate):
    """
    Saves a CandidateData object into MongoDB.
    """
    if candidates_col.find_one({"email": candidate.email}):
        return "Candidate already exists in DB."
    else:
        candidates_col.insert_one(candidate.dict())
        return "Candidate saved to MongoDB."

def save_candidate_response(candidate_id, question, answer):
    """
    Saves a candidate's response to a question (without evaluation)
    """
    responses_col.insert_one({
        "candidate_id": candidate_id,
        "question": question,
        "answer": answer,
        "timestamp": datetime.now()
    })
    return "Response saved."

def save_candidate_evaluated_response(candidate_id, question, answer, rating, timestamp=None):
    """
    Saves a candidate's response along with its LLM evaluation
    
    Args:
        candidate_id: The candidate's ID
        question: The interview question
        answer: The candidate's answer
        rating: Numerical rating (1-5)
        timestamp: Optional timestamp (defaults to current time)
    
    Returns:
        Status message
    """
    if timestamp is None:
        timestamp = datetime.now()
    elif isinstance(timestamp, str):
        try:
            timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            timestamp = datetime.now()
            
    # Ensure rating is within bounds
    try:
        rating = int(rating)
        rating = max(1, min(5, rating))
    except (ValueError, TypeError):
        rating = 0
        
    evaluated_responses_col.insert_one({
        "candidate_id": candidate_id,
        "question": question,
        "answer": answer,
        "rating": rating,
        "timestamp": timestamp
    })
    
    return "Evaluated response saved."
