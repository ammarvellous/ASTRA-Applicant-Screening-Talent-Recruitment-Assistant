# db_utils.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongo_uri)
db = client["talentscout"]
candidates_col = db["candidates"]

def save_candidate(candidate):
    """
    Saves a CandidateData object into MongoDB.
    """
    candidates_col.insert_one(candidate.dict())
    print("Candidate saved to MongoDB.")

