# app.py
import streamlit as st
from datetime import datetime
import re
from io import BytesIO
from db_utils import save_candidate

# Optional libs for parsing (install if needed)
try:
    import PyPDF2
except Exception:
    PyPDF2 = None

try:
    import docx
except Exception:
    docx = None

# ---------- Config ----------
st.set_page_config(page_title="ASTRA-Applicant-Screening-Talent-Recruitment-Assistant", layout="centered")

TECH_KEYWORDS = [
    # Add / extend as needed
    "python","django","flask","fastapi","javascript","typescript","react","angular",
    "vue","node","express","java","spring","kotlin","golang","go","c#","c++",
    "aws","azure","gcp","docker","kubernetes","postgres","mysql","mongodb",
    "redis","graphql","rest","sql","tensorflow","pytorch","keras","spark"
]

CONVERSATION_END_KEYWORDS = ["exit","quit","bye","goodbye","thanks","thank you","stop"]

# ---------- Helpers ----------
def extract_text_from_pdf(bytes_data):
    if PyPDF2 is None:
        return ""
    text = []
    reader = PyPDF2.PdfReader(BytesIO(bytes_data))
    for page in reader.pages:
        try:
            text.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(text)

def extract_text_from_docx(bytes_data):
    if docx is None:
        return ""
    tmp_path = "/tmp/_tmp_docx.docx"
    with open(tmp_path, "wb") as f:
        f.write(bytes_data)
    doc = docx.Document(tmp_path)
    paras = [p.text for p in doc.paragraphs if p.text]
    return "\n".join(paras)

def extract_text_from_txt(bytes_data):
    try:
        return bytes_data.decode("utf-8", errors="ignore")
    except:
        return str(bytes_data)

EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"(\+\d{1,3}[\s-]?)?(\(?\d{2,4}\)?[\s-]?)?[\d\s-]{6,15}")

def autofill_fields_from_text(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    name = lines[0] if lines else ""
    email_match = EMAIL_RE.search(text)
    phone_match = PHONE_RE.search(text)
    email = email_match.group(0) if email_match else ""
    phone = phone_match.group(0) if phone_match else ""
    # Try to detect tech stack using keywords
    lowered = text.lower()
    detected_tech = sorted({k for k in TECH_KEYWORDS if k in lowered}, key=lambda x: lowered.find(x))
    # Try to estimate years of experience: look for patterns like 'X years'
    years = None
    ymatch = re.search(r"(\d{1,2})\+?\s+years", lowered)
    if ymatch:
        years = int(ymatch.group(1))
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "location": "",
        "years_experience": years if years is not None else 0,
        "tech_stack": detected_tech
    }

# ---------- UI ----------
st.title("ASTRA-Applicant-Screening-Talent-Recruitment-Assistant (Setup)")
st.write("Welcome! Choose how to provide candidate details — manually, or upload a resume to autofill.")

choice = st.radio("Get started by:", ("Manual fill", "Autofill from resume (upload)"))

# Candidate state holder
if "candidate" not in st.session_state:
    st.session_state.candidate = {
        "name": "",
        "email": "",
        "phone": "",
        "location": "",
        "years_experience": 0,
        "desired_positions": [],
        "tech_stack": []
    }
if "raw_resume_text" not in st.session_state:
    st.session_state.raw_resume_text = ""

if choice == "Autofill from resume (upload)":
    st.subheader("Upload resume (PDF / DOCX / TXT)")
    uploaded = st.file_uploader("Choose a resume file", type=["pdf","docx","txt"])
    if uploaded is not None:
        raw = uploaded.read()
        st.session_state.raw_resume_text = "" # for debugging purposes only
        parsed_text = ""
        if uploaded.type == "application/pdf" or uploaded.name.lower().endswith(".pdf"):
            if PyPDF2 is None:
                st.warning("PyPDF2 not installed — install with `pip install PyPDF2` for PDF parsing. Falling back to raw bytes display.")
            parsed_text = extract_text_from_pdf(raw) if PyPDF2 else ""
        elif uploaded.name.lower().endswith(".docx"):
            if docx is None:
                st.warning("python-docx not installed — install with `pip install python-docx` for docx parsing.")
            parsed_text = extract_text_from_docx(raw) if docx else ""
        else:
            parsed_text = extract_text_from_txt(raw)
        st.session_state.raw_resume_text = parsed_text

        from resume_parser import parse_resume_to_json
        from pydantic import ValidationError

        # after extracting resume text
        try:
            candidate = parse_resume_to_json(parsed_text)
            print(candidate.dict())
            st.json(candidate.dict())   # just to preview
            # candidate.dict() can be stored directly in MongoDB

        except ValidationError as ve:
            st.error(f"Validation failed: {ve}")

        # Save to MongoDB
        save_candidate(candidate)
        st.success("Candidate saved successfully!")
        
        # Store in session for further chat
        st.session_state.candidate = candidate

        if not parsed_text.strip():
            st.info("No text was extracted — you can still paste resume text below or fill fields manually.")
        else:
            st.success("Parsed resume text")
            st.text_area("Parsed resume", parsed_text, height=200)
            # Autofill
            autofill = autofill_fields_from_text(parsed_text)
            st.session_state.candidate.update({
                "name": autofill["name"],
                "email": autofill["email"],
                "phone": autofill["phone"],
                "location": autofill["location"],
                "years_experience": autofill["years_experience"],
                "tech_stack": autofill["tech_stack"]
            })
    else:
        st.info("Upload a resume to try autofill. Or switch to Manual fill.")

if choice == "Manual fill" or True:
    st.subheader("Candidate details (review & edit)")

    c = st.session_state.candidate
    # Simple form for candidate info
    with st.form("candidate_form"):
        c["name"] = st.text_input("Full name", value=c.get("name",""))
        c["email"] = st.text_input("Email", value=c.get("email",""))
        c["phone"] = st.text_input("Phone", value=c.get("phone",""))
        c["location"] = st.text_input("Current location", value=c.get("location",""))
        c["years_experience"] = st.number_input("Years of experience", min_value=0, max_value=60, value=int(c.get("years_experience",0)))
        desired = st.text_input("Desired position(s) (comma-separated)", value=",".join(c.get("desired_positions",[])))
        tech_text = st.text_input("Tech stack (comma-separated)", value=",".join(c.get("tech_stack",[])))
        consent = st.checkbox("I consent to storing my information for recruitment purposes.", value=True)
        submitted = st.form_submit_button("Save & Generate Screening Questions")

    if submitted:
        if not consent:
            st.error("Consent required.")
        else:
            c["desired_positions"] = [p.strip() for p in desired.split(",") if p.strip()]
            c["tech_stack"] = [t.strip() for t in tech_text.split(",") if t.strip()]
            st.session_state.candidate = c
            st.success("Candidate information saved to session. Next: question generation or review.")
            st.markdown("**Candidate summary:**")
            st.write({
                "name": c["name"],
                "email": c["email"],
                "phone": c["phone"],
                "location": c["location"],
                "years_experience": c["years_experience"],
                "desired_positions": c["desired_positions"],
                "tech_stack": c["tech_stack"]
            })
            # Placeholder: call your question generator here or navigate to screening flow
            st.info("Now you can use this info to generate technical questions (LLM or heuristics).")

# Shortcuts & tips
st.write("---")
st.subheader("Notes & next steps")
st.markdown("""
- You can store the `st.session_state.candidate` into MongoDB Atlas (example commented in next section).
""")

# Export candidate JSON
if st.button("Download candidate JSON"):
    st.download_button("Download JSON", str(st.session_state.candidate), file_name="candidate.json")

# ---------- Example: where to plug LLM-based parsing or DB ----------
st.write("---")
st.subheader("Integration hints (developer)")
st.markdown("""

- **Saving to MongoDB Atlas**: use `pymongo`. Store candidate doc in `candidates` and transcripts in `transcripts`. Do **not** store API keys or secrets in the transcript.

- **Context-aware chat**: for multi-turn, use LangChain to manage chains and memory, or keep a short conversation window and pass a summarized candidate profile to the LLM on every chat call.
""")