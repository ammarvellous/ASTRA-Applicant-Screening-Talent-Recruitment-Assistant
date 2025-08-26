# 🧑‍💼 ASTRA – AI-Powered Applicant Screening & Talent Recruitment Assistant  

ASTRA is an **AI-driven recruitment assistant** that:  
- Parses resumes into structured candidate profiles.  
- Stores candidate data securely in a **MongoDB Atlas** database.  
- Provides an **interactive interview chatbot** with context-aware questioning.  
- Helps recruiters screen, evaluate, and rank applicants efficiently.  

Built with **Streamlit + LangChain + Gemini/WatsonX LLMs**.  

---

## ✨ Features  
- 📄 **Resume Parsing** – Upload a resume (PDF/DOC/TXT) → get structured JSON.  
- 🗄️ **Database Integration** – Candidate profiles saved in MongoDB Atlas.  
- 💬 **Interactive Interview** – Multi-turn chatbot asks technical, project, and job-specific questions.  
- 🧠 **Context Awareness** – Questions adapt to candidate’s skills & resume.  
- ⏱️ **Timed Sections** – (Optional) auto-progressing interview flow.  
- 📊 **Recruiter View** – Review parsed JSON, candidate details, and interview logs.  

---

## 🛠️ Tech Stack  
- [**Streamlit**](https://streamlit.io) – UI framework  
- [**LangChain**](https://www.langchain.com/) – LLM orchestration & memory  
- [**Google Gemini**](https://ai.google.dev/) / [**IBM WatsonX**](https://www.ibm.com/watsonx) – LLMs for parsing & Q&A  
- [**MongoDB Atlas**](https://www.mongodb.com/atlas) – Candidate data storage  
- [**Pydantic**](https://docs.pydantic.dev/) – Candidate schema validation  

---

## 📂 Project Structure  
ASTRA-Applicant-Screening-Talent-Recruitment-Assistant/
│
├── app.py # Main Streamlit app (UI, chatbot, flow control)
├── resume_parser.py # Resume → CandidateData parser
├── db_handler.py # MongoDB Atlas integration
├── interview_flow.py # (Optional) Interview Q&A logic
│
├── requirements.txt # Python dependencies
└── README.md # Project documentation


---

## ⚡ Quickstart  

### 1️⃣ Clone Repository  
```bash
git clone https://github.com/yourusername/ASTRA-Applicant-Screening-Talent-Recruitment-Assistant.git
cd ASTRA-Applicant-Screening-Talent-Recruitment-Assistant
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Set Up Environment

Create a .env file with:
```bash
MONGODB_URI="your-mongodb-atlas-uri"
GOOGLE_API_KEY="your-gemini-api-key"
WATSONX_API_KEY="your-watsonx-api-key"
```
4️⃣ Run App
```bash
streamlit run app.py
```

💡 Usage Flow

Upload Resume → Candidate profile extracted (JSON + UI view).

Save to Database → Profile stored in MongoDB Atlas.

Start Interview → Interactive Q&A with AI interviewer.

Review Session → Recruiter sees answers & ratings.

🚀 Roadmap

✅ Resume parsing

✅ MongoDB storage

✅ Interactive interview chatbot

🔲 Recruiter dashboard (candidate ranking)

🔲 Job description matching (JD ↔ Candidate fit)

🔲 Export candidate reports (PDF/CSV)

🤝 Contributing

PRs and feature requests are welcome!

📜 License

MIT License © 2025 YourName
