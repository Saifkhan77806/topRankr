JD_SCHEMA = """ 
                {
                    "role":"",
                    "experience_years":0,
                    "industry":"",
                    "seniority":"",
                    "skills":{
                        "required":[],
                        "preferred":[]
                    },
                    "responsibilities":[],
                    "education":[],
                    "domain":[]
                }
            """


def build_jd_prompt(jd: str):

    return f"""
                You are an expert recruiter.

                Analyze this job description.

                Return ONLY valid JSON.

                Schema:

                {JD_SCHEMA}

                Job Description:

                {jd}
            """