# app.py
import streamlit as st
from db_utils import save_candidate
from helpers import *
from interview import start_interview

# ---------- Config ----------
st.set_page_config(page_title="ASTRA-Applicant-Screening-Talent-Recruitment-Assistant", layout="centered")

# ---------- UI ----------
st.title("ASTRA-Applicant-Screening-Talent-Recruitment-Assistant")

st.write("Welcome! Choose how to provide candidate details — manually, or upload a resume to autofill.")

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

# Add a flag to track if candidate has been saved to DB
if "candidate_saved_to_db" not in st.session_state:
    st.session_state.candidate_saved_to_db = False

with st.expander("1. Upload resume (PDF / DOCX / TXT)", expanded=True): 
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
            # Parse the resume into a CandidateData object
            candidate_data = parse_resume_to_json(parsed_text)
            st.json(candidate_data.model_dump())
            
            # Save to MongoDB only if not already saved
            if not st.session_state.candidate_saved_to_db:
                result = save_candidate(candidate_data)
                print(result)
                st.session_state.candidate_saved_to_db = True
            
            # Store in session state as a dictionary for consistency
            st.session_state.candidate = candidate_data.model_dump()
            
            if not parsed_text.strip():
                st.info("No text was extracted — you can still paste resume text below or fill fields manually.")
            else:
                st.success("Parsed resume text")
                st.text_area("Parsed resume", parsed_text, height=200)
                
                # Get autofill data
                autofill = autofill_fields_from_text(parsed_text)
                
                # Update the dictionary in session state directly
                st.session_state.candidate.update({
                    "name": autofill["name"] if not st.session_state.candidate.get("name") else st.session_state.candidate["name"],
                    "email": autofill["email"] if not st.session_state.candidate.get("email") else st.session_state.candidate["email"],
                    "phone": autofill["phone"] if not st.session_state.candidate.get("phone") else st.session_state.candidate["phone"],
                    "location": autofill["location"] if not st.session_state.candidate.get("location") else st.session_state.candidate["location"],
                    "years_experience": autofill["years_experience"] if not st.session_state.candidate.get("years_experience") else st.session_state.candidate["years_experience"],
                    "tech_stack": autofill["tech_stack"] if not st.session_state.candidate.get("tech_stack") else st.session_state.candidate["tech_stack"]
                })

        except ValidationError as ve:
            st.error(f"Validation failed: {ve}")
    else:
        st.info("Upload a resume to try autofill. Or switch to Manual fill.")

st.write("---")
with st.expander("2. Candidate details (review & edit)", expanded=False):
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
        submitted = st.form_submit_button("Submit Data")

    if submitted:
        if not consent:
            st.error("Consent required.")
        else:
            c["desired_positions"] = [p.strip() for p in desired.split(",") if p.strip()]
            c["tech_stack"] = [t.strip() for t in tech_text.split(",") if t.strip()]
            st.session_state.candidate = c
            
            # Save to database only if this is new data (manual entry)
            if not st.session_state.candidate_saved_to_db:
                from resume_parser import CandidateData
                try:
                    candidate_obj = CandidateData(**c)
                    message, candidate_id = save_candidate(candidate_obj)
                    st.session_state.candidate["_id"] = candidate_id  # Store the ID
                    st.session_state.candidate_saved_to_db = True
                    st.success(message)
                except Exception as e:
                    st.error(f"Error saving to database: {e}")
            
            st.success("Candidate information saved.")
            st.markdown("**Candidate summary:**")
            st.write({
                "name": c["name"],
                "email": c["email"],
                "phone": c["phone"],
                "location": c["location"],
                "years_experience": c["years_experience"],
                "desired_positions": c["desired_positions"],
                "tech_stack": c["tech_stack"] if c["tech_stack"] else []
            })
            # Placeholder: call your question generator here or navigate to screening flow
            st.info("Please proceed to next section!")

    # Export candidate JSON
    if st.button("Download candidate JSON"):
        st.download_button("Download JSON", str(st.session_state.candidate), file_name="candidate.json")

st.write("---")
with st.expander("3. Start technical interview", expanded=False):
    st.write("---")
    st.write("---")
    st.header("Technical Interview")

    # Initialize session state keys
    if "candidate" not in st.session_state:
        st.session_state.candidate = None

    if "interview_started" not in st.session_state:
        st.session_state.interview_started = False

    if "interview_progress" not in st.session_state:
        st.session_state.interview_progress = 0

    if "interview_consent" not in st.session_state:
        st.session_state.interview_consent = False

    if st.session_state.candidate:
        st.success("Candidate information ready for interview.")
        
        if not st.session_state.interview_started:
            # Interview instructions in a nice container
            with st.container():
                st.subheader("📝 Interview Instructions")
                
                st.markdown("""
                ### Please read carefully before proceeding
                
                **Interview Process:**
                - This is an automated technical screening interview
                - Questions will be based on your resume and tech stack
                - The entire session will be approximately 15-20 minutes
                
                **Important Guidelines:**
                - ⏱️ You will have **60 seconds** to answer each question
                - ⛔ There will be **no pause button** once the interview begins
                - 🎥 Your responses will be recorded and evaluated
                - 🔄 Please answer each question before proceeding to the next
                - 📊 Your performance will be scored based on accuracy and completeness
                
                **Technical Requirements:**
                - Ensure your microphone is working properly
                - A stable internet connection is required
                - Browser permissions for microphone access must be granted
                
                **Privacy Notice:**
                Your responses will be processed to evaluate your technical skills. The data will be handled in accordance with our privacy policy.
                """)
                
                # Consent checkbox
                interview_consent = st.checkbox("I have read and understood the instructions and am ready to proceed with the timed interview.", key="interview_consent_checkbox")
                
                # Start button - only enabled if consent is given
                start_col1, start_col2, start_col3 = st.columns([1,2,1])
                with start_col2:
                    if interview_consent:
                        st.session_state.interview_consent = True
                        st.button("🎬 Start Interview", 
                                type="primary",
                                help="Click to begin the timed interview. Make sure you're ready!",
                                on_click=lambda: setattr(st.session_state, "interview_started", True))
                    else:
                        # Disabled button with tooltip
                        st.markdown("""
                        <div title="Please confirm you've read the instructions first" style="opacity:0.6;">
                        <button disabled style="width:100%;padding:0.5rem;background:#cccccc;color:#666666;border-radius:4px;border:none;cursor:not-allowed;">
                            🎬 Start Interview
                        </button>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.caption("⚠️ Please check the box above to enable the Start button")
        
        # Start the interview if the user has clicked the button
        if st.session_state.interview_started:
            start_interview(st.session_state.candidate)
    else:
        st.info("Please complete your candidate profile before starting the interview.")

st.write("---")
#while the interview is initialiazing give the user a loader for it
# ---------- Greeting ----------
st.subheader("Thank you!!!")
st.markdown("""
            Thank you for completing the interview process!
            We will be in touch with you shortly.
            """)