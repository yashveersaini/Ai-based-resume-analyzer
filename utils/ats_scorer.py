import os
import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


def get_gemini_model():
    """Initialize and return Gemini 2.5 Flash model."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1,
        google_api_key=api_key
    )


# System prompt for ATS analysis
SYSTEM_PROMPT = """You are an expert ATS (Applicant Tracking System) and Resume Analyzer.
You will be given a RESUME and a JOB DESCRIPTION.
Evaluate and return ONLY a JSON response with these fields:
{{
  "overall_score": <weighted average out of 100>,
  "tone_style_score": <0-100>,
  "content_score": <0-100>,
  "structure_score": <0-100>,
  "skills_score": <0-100>,
  "ats_score": <0-100>,
  "missing_keywords": ["keyword1", "keyword2", ...],
  "improvements": {{
    "tone_style": ["suggestion1", "suggestion2"],
    "content": ["suggestion1", "suggestion2"],
    "structure": ["suggestion1", "suggestion2"],
    "skills": ["suggestion1", "suggestion2"],
    "ats": ["suggestion1", "suggestion2"]
  }},
  "matched_skills": ["skill1", "skill2", ...],
  "missing_skills": ["skill1", "skill2", ...]
}}

Scoring Guidelines:
- tone_style_score (20%): Professional language, action verbs, clear communication
- content_score (30%): Semantic match, relevant experience, keyword alignment
- structure_score (15%): Formatting, sections, readability, organization
- skills_score (25%): Technical and soft skills match with JD requirements
- ats_score (10%): Machine parsability, standard sections, keyword optimization

Overall score calculation:
overall_score = (tone_style_score × 0.20) + (content_score × 0.30) + (structure_score × 0.15) + (skills_score × 0.25) + (ats_score × 0.10)

Return ONLY minified JSON. No explanation, no markdown, no extra text."""


def analyze_resume(resume_text: str, job_description: str) -> dict:
    """
    Analyze resume against job description using Gemini 2.5 Flash.
    
    Args:
        resume_text: Full text content of the resume
        job_description: Job description text to compare against
    
    Returns:
        dict: Complete ATS analysis with scores, keywords, and suggestions
    """
    try:
        llm = get_gemini_model()
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "=== RESUME ===\n{resume_text}\n\n=== JOB DESCRIPTION ===\n{job_description}")
        ])
        
        chain = prompt | llm
        
        response = chain.invoke({
            "resume_text": resume_text[:8000],  # Limit to 8k chars to avoid token limit
            "job_description": job_description[:3000]  # Limit JD to 3k chars
        })
        
        content = response.content
        
        content = re.sub(r'^```json\s*', '', content.strip())
        content = re.sub(r'\s*```$', '', content.strip())
        
        result = json.loads(content)
        
        required_fields = [
            "overall_score", "tone_style_score", "content_score", 
            "structure_score", "skills_score", "ats_score"
        ]
        
        for field in required_fields:
            if field not in result:
                result[field] = 0
        
        # Ensure lists exist
        if "missing_keywords" not in result:
            result["missing_keywords"] = []
        if "matched_skills" not in result:
            result["matched_skills"] = []
        if "missing_skills" not in result:
            result["missing_skills"] = []
        if "improvements" not in result:
            result["improvements"] = {
                "tone_style": [],
                "content": [],
                "structure": [],
                "skills": [],
                "ats": []
            }
        
        for key in required_fields:
            if isinstance(result[key], (int, float)):
                result[key] = round(float(result[key]))
        
        return result
    
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")
        print(f"Response content: {content[:500]}")
        return get_fallback_response()
    
    except Exception as e:
        print(f"ATS Analysis Error: {e}")
        return get_fallback_response()


def get_fallback_response() -> dict:
    """Return a fallback response if API fails."""
    return {
        "overall_score": 0,
        "tone_style_score": 0,
        "content_score": 0,
        "structure_score": 0,
        "skills_score": 0,
        "ats_score": 0,
        "missing_keywords": [],
        "matched_skills": [],
        "missing_skills": [],
        "improvements": {
            "tone_style": ["Unable to analyze. Please try again."],
            "content": ["Unable to analyze. Please try again."],
            "structure": ["Unable to analyze. Please try again."],
            "skills": ["Unable to analyze. Please try again."],
            "ats": ["Unable to analyze. Please try again."]
        },
        "error": "Analysis failed. Please check your API key and try again."
    }


def compute_ats_score(resume_text: str, job_description: str) -> dict:
    """
    Backward compatible wrapper for analyze_resume().
    Maintains same function signature as old version.
    """
    return analyze_resume(resume_text, job_description)