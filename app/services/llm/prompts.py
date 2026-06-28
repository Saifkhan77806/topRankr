CANDIDATE_PROFILE_SCHEMA = """
{
  "personal": {
    "name": "",
    "email": "",
    "phone": "",
    "location": ""
  },

  "professional": {
    "current_title": "",
    "total_experience_years": 0,
    "industry": "",
    "seniority": "",
    "domain_expertise": []
  },

  "skills": {
    "technical": [],
    "tools": [],
    "soft_skills": [],
    "languages": []
  },

  "education": [
    {
      "degree": "",
      "field": "",
      "institution": "",
      "year": ""
    }
  ],

  "experience": [
    {
      "company": "",
      "role": "",
      "duration": "",
      "description": "",
      "skills_used": []
    }
  ],

  "projects": [
    {
      "name": "",
      "description": "",
      "technologies": []
    }
  ],

  "certifications": [],

  "leadership": {
    "has_leadership": false,
    "team_size": 0,
    "management_experience": false
  },

  "achievements": []
}
"""


def build_resume_prompt(resume_text: str):

    return f"""
You are an expert recruiter.

Extract information from this resume.

Rules:

1. Return ONLY valid JSON.
2. Do not explain anything.
3. If information is missing use null.
4. Infer industry.
5. Infer seniority.

Return EXACTLY this schema:

{CANDIDATE_PROFILE_SCHEMA}

Resume:

{resume_text[:15000]}
"""