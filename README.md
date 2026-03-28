# 🚀 ResumeIQ – AI-Based Resume Analyzer & Job Role Suggestion System

## 📌 Brief One Line Summary  
An AI-powered web application that analyzes resumes, evaluates ATS compatibility with actionable improvement insights and recommends suitable job roles .

https://github.com/user-attachments/assets/e21c357a-6e18-44d9-8889-c7a6f0307784


---

## 📖 Overview  
ResumeIQ is designed to help job seekers optimize their resumes and identify the most suitable job roles based on their skills and experience. The system leverages Natural Language Processing (NLP), AI and Machine Learning to compare resumes with job descriptions, calculate ATS (Applicant Tracking System) scores, and provide personalized suggestions.

---

## ❗ Problem Statement  
Many candidates face rejection due to poorly optimized resumes that fail ATS screening. Additionally, candidates often lack clarity about which job roles best match their skillset.  

This project solves:
- Low ATS compatibility of resumes  
- Lack of personalized resume feedback  
- Difficulty in identifying suitable job roles  

---

## 📂 Dataset  
- Job descriptions dataset (various roles and industries)  
- Resume samples for training and testing  
- Custom processed text data for NLP tasks (tokenization, vectorization)

---

## 🛠 Tools and Technologies  
- **Backend:** Python, Flask  
- **Database:** PostgreSQL  
- **Machine Learning:** Scikit-learn, Logistics regression  
- **NLP:** TF-IDF, text preprocessing, similarity matching  
- **AI/LLM:** LangChain, Gemini API (GenAI)  
- **Frontend:** HTML, CSS, JavaScript  
- **Authentication:** User login & session management  

---

## ⚙️ Methods  
- Resume and job description parsing using NLP techniques  
- Text vectorization (TF-IDF) for converting text to vector
- ATS score calculation based on keyword matching and relevance  
- Hybrid recommendation system:
  - Machine Learning model for prediction  
  - Rule-based mapping for accuracy improvement  
- Integration with GenAI (Gemini API) for smart suggestions  

---

## 💡 Key Insights  
- Identifies missing skills and keywords in resumes  
- Provides actionable suggestions to improve ATS score  
- Helps users understand how closely their resume matches job descriptions  
- Recommends job roles aligned with candidate profiles  

---

## 📊 Dashboard / Model / Output     
- ## **User-friendly dashboard for real-time interaction**  

<img width="1827" height="792" alt="image" src="https://github.com/user-attachments/assets/91468c11-1ad7-448c-8b7e-e99c324dd980" />

<img width="1806" height="806" alt="image" src="https://github.com/user-attachments/assets/fedf6555-242e-4e77-87e5-6a1abc119f49" />

<img width="1666" height="825" alt="image" src="https://github.com/user-attachments/assets/2ac73f55-bdb7-482a-9049-9571cfda0818" />

- ## **ATS compatibility score (percentage-based)**
  
<img width="1692" height="823" alt="image" src="https://github.com/user-attachments/assets/f2823cb2-53b6-474a-8005-d5b3022605c7" />

- ## **Skill gap analysis**

<img width="1693" height="833" alt="image" src="https://github.com/user-attachments/assets/0d8988fb-13be-4ee0-892d-d5c6dd216f4f" />

- ## **Resume improvement suggestions**
<img width="1671" height="820" alt="image" src="https://github.com/user-attachments/assets/55bd605b-738e-4069-8a66-51e219b2de20" />
<img width="1691" height="771" alt="image" src="https://github.com/user-attachments/assets/b05cad3d-0f36-4fcf-b221-9d028d49f76f" />

- ## **Predicted job roles with confidence score**
<img width="1573" height="797" alt="image" src="https://github.com/user-attachments/assets/f0363b4d-47a5-413e-8409-8641c6f5db3c" /> 
  
<img width="1668" height="811" alt="image" src="https://github.com/user-attachments/assets/4fa0ef64-9f38-4952-b0ab-712f352e9b46" />

---

## ▶️ How to Run this Project on Local system?  

### 1. Clone the repository  
```bash
git clone https://github.com/yashveersaini/Ai-based-resume-analyzer.git
cd Ai-based-resume-analyzer
```

### 2. Create virtual environment  
```bash
python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)
```

### 3. Install dependencies  
```bash
pip install -r requirements.txt
```

### 4. Setup database  
- Install PostgreSQL  
- Create a database (e.g., `resumeiq_db`)  
- Update database credentials in your configuration file (`config.py` or `.env`)  

Example:
```bash
DB_NAME=resumeiq
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Setup Environment Variables (for AI integration)  
- Add your Gemini API key  

Example:
```bash
GEMINI_API_KEY=your_api_key_here
```

- Add Cloudinary API key

Example:
```bash
CLOUDINARY_CLOUD_NAME = 'your_cloud_name'
CLOUDINARY_API_KEY = 'your_api_key'
CLOUDINARY_API_SECRET = 'Your_api_secret'
```

### 6. Run the application  
```bash
python app.py
```

### 7. Open in browser  
http://127.0.0.1:5000/

---

## 📈 Results & Conclusion  
- Achieved **~95% accuracy** in job role prediction using a hybrid recommendation system  
- Improved resume-job matching efficiency using NLP-based similarity scoring  
- Provided actionable suggestions to enhance ATS compatibility  
- Built a scalable and user-friendly full-stack AI application  

---

## 🔮 Future Work  
- Support advanced resume parsing (PDF, DOCX with better accuracy)  
- Integrate more powerful LLMs for deeper analysis  
- Add recruiter dashboard for candidate filtering  
- Deploy on cloud platforms (AWS/GCP)  
- Implement real-time job scraping and recommendations  
