import streamlit as st
import time
import random
import os
from datetime import datetime
from db_utils import save_candidate_response
from question_generator import generate_tech_questions, generate_project_questions, generate_job_questions
import streamlit.components.v1 as components

def save_answer(candidate, question, answer):
    """Save answer to session state and optionally to database"""
    if "answers" not in st.session_state:
        st.session_state.answers = []
    
    st.session_state.answers.append({
        "candidate": candidate['name'],
        "question": question,
        "answer": answer,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # Optionally save to database if candidate_id is available
    if "candidate_id" in candidate:
        save_candidate_response(candidate["candidate_id"], question, answer)

def initialize_interview():
    """Initialize interview state if not already done"""
    if "interview_questions" not in st.session_state:
        # Get candidate info
        candidate = st.session_state.candidate
        
        # Generate tech questions (1-2)
        tech_questions = []
        if "tech_stack" in candidate and candidate["tech_stack"]:
            all_tech_q = generate_tech_questions(candidate)
            tech_questions = random.sample(all_tech_q, min(2, len(all_tech_q)))
        
        # Generate project questions (1-2)
        project_questions = []
        if "projects" in candidate and candidate["projects"]:
            all_proj_q = generate_project_questions(candidate)
            project_questions = random.sample(all_proj_q, min(2, len(all_proj_q)))
        
        # Generate job role questions (1-2)
        job_role = "Software Engineer"
        job_questions = generate_job_questions(job_role)
        
        # Combine all questions
        st.session_state.interview_questions = tech_questions + project_questions + job_questions
        st.session_state.current_question_index = 0
        st.session_state.interview_stage = "tech"
        st.session_state.current_answer = ""
        st.session_state.interview_completed = False
        st.session_state.time_limit = 5.0  # 5 seconds for testing
        st.session_state.start_time = None

def start_interview(candidate):
    """Main interview function"""
    # Initialize interview if needed
    initialize_interview()
    print(f"Interview Questions: {st.session_state.interview_questions}")  # Debugging line
    
    # Display interview progress
    total_questions = len(st.session_state.interview_questions)
    current_index = st.session_state.current_question_index
    
    # Interview progress indicator
    progress_text = f"Question {current_index + 1} of {total_questions}"
    progress_value = (current_index + 1) / total_questions
    
    st.progress(progress_value, text=progress_text)
    
    # Interview completed case
    if st.session_state.interview_completed:
        show_interview_summary()
        return
    
    # Get current question
    if current_index < total_questions:
        current_question = st.session_state.interview_questions[current_index]
        
        # Show appropriate section header based on question type
        if current_index == 0:
            st.subheader("💻 Technical Skills Questions")
        elif current_index == len(st.session_state.interview_questions) - len(generate_job_questions("any")):
            st.subheader("🏢 Job Role Questions")
        elif st.session_state.interview_stage == "tech" and "projects" in candidate and candidate["projects"]:
            st.subheader("📋 Project Experience Questions")
            st.session_state.interview_stage = "project"
        
        # Display question
        st.write(f"**Question {current_index + 1}:** {current_question}")
        
        # Initialize timer for this question if needed
        if st.session_state.start_time is None:
            st.session_state.start_time = time.time()
            st.session_state.current_answer = ""
        
        
        # Timer progress bar
        st.markdown("""
            <script>
            let limit = 30;
            function startTimer() {
                let timer = setInterval(function() {
                    document.getElementById("timer").innerHTML = "⏱️ " + limit + "s left";
                    limit -= 1;
                    if (limit < 0) clearInterval(timer);
                }, 1000);
            }
            </script>
            <div id="timer">⏱️ 30s left</div>
            <script>startTimer();</script>
        """, unsafe_allow_html=True)

        # Answer input
        answer = st.text_area("Your answer:", 
                             value=st.session_state.current_answer,
                             height=150,
                             key=f"answer_{current_index}")
        
        # Update current answer in session state
        st.session_state.current_answer = answer
        
        # Check if time's up
        if elapsed >= st.session_state.time_limit:
            if not st.session_state.get(f"submitted_{current_index}", False):
                st.warning("Time's up! Moving to next question...")
                
                # Save answer
                save_answer(candidate, current_question, answer)
                
                # Move to next question
                st.session_state[f"submitted_{current_index}"] = True
                st.session_state.current_question_index += 1
                st.session_state.start_time = None  # Reset timer for next question
                st.rerun()
        
        # Allow manual submission
        if st.button("Submit Answer", key=f"submit_{current_index}"):
            # Save answer
            save_answer(candidate, current_question, answer)
            
            # Move to next question
            st.session_state[f"submitted_{current_index}"] = True
            st.session_state.current_question_index += 1
            st.session_state.start_time = None  # Reset timer for next question
            st.rerun()
    else:
        # All questions answered, mark interview as completed
        st.session_state.interview_completed = True
        show_interview_summary()

def show_interview_summary():
    """Display summary of interview responses"""
    st.success("🎉 Interview completed!")
    
    st.subheader("Interview Summary")
    st.write("Thank you for completing the interview. Your responses have been recorded.")
    
    # Show answers summary
    if "answers" in st.session_state and st.session_state.answers:
        for i, qa in enumerate(st.session_state.answers):
            with st.expander(f"Question {i+1}: {qa['question']}"):
                st.write("**Your answer:**")
                st.write(qa["answer"])
    
    # Reset button
    if st.button("Start New Interview"):
        # Clear interview state
        for key in ["interview_questions", "current_question_index", 
                   "start_time", "current_answer", 
                   "interview_completed", "interview_stage"]:
            if key in st.session_state:
                del st.session_state[key]
        
        # Clear submissions
        for key in list(st.session_state.keys()):
            if key.startswith("submitted_"):
                del st.session_state[key]
                
        st.rerun()
