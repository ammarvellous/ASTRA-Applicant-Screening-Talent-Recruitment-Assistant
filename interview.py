import streamlit as st
import time

# Example question bank (later you’ll generate dynamically)
QUESTION_BANK = [
    "What is Python's GIL?",
    "Explain Django's ORM.",
    "How do you optimize a slow SQL query?",
    "Describe a project where you solved a scaling issue.",
    "How would you design a REST API for a social media app?"
]

def save_answer(candidate, question, answer):
    # Later: save to MongoDB with candidate ID
    if "answers" not in st.session_state:
        st.session_state.answers = []
    st.session_state.answers.append({
        "candidate": candidate['name'],
        "question": question,
        "answer": answer
    })

def start_interview(candidate):
    progress = st.session_state.interview_progress

    if progress < len(QUESTION_BANK):
        question = QUESTION_BANK[progress]

        with st.expander(f"Question {progress + 1}", expanded=True):
            st.write(question)
            answer = st.text_area("Your Answer", key=f"answer_{progress}")

            # Manual Next Button
            if st.button("Next Question", key=f"next_{progress}"):
                save_answer(candidate, question, answer)
                st.session_state.interview_progress += 1
                st.rerun()

            # Timer Auto-Advance
            countdown_placeholder = st.empty()
            for i in range(10, 0, -1):  # 10-second timer
                countdown_placeholder.info(f"Auto-next in {i}s")
                time.sleep(1)

            save_answer(candidate, question, answer)
            st.session_state.interview_progress += 1
            st.rerun()

    else:
        st.success("Interview completed ✅")
        st.write("Thank you for your time!")