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
        st.warning("Candidate already exists in DB.")
    else:
        candidates_col.insert_one(candidate.dict())
        print("Candidate saved to MongoDB.")
