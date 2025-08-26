# db_utils.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongo_uri)
db = client["Astra"]
candidates_col = db["candidates"]

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
    db.responses.insert_one({
        "candidate_id": candidate_id,
        "question": question,
        "answer": answer
    })
