import os
import json

from openai import OpenAI


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv(
        "OPENROUTER_API_KEY"
    )
)


def build_candidates(
        candidates
):

    text = ""

    for candidate in candidates:

        profile = candidate["profile"]

        text += f"""

            Candidate ID:
            {candidate["candidate_id"]}

            Name:
            {candidate["name"]}

            Current Role:
            {candidate["title"]}

            Industry:
            {candidate["industry"]}

            Experience:
            {
            profile
            .get(
                "professional",
                {}
            )
            .get(
                "total_experience_years",
                0
            )
            }

            Skills:
            {
            profile
            .get(
                "skills",
                {}
            )
            }

            Leadership Score:
            {
            candidate["scores"]
            ["leadership"]
            }

            Ranking Score:
            {
            candidate["ranking_score"]
            }

        """

    return text


def rerank_candidates(

        jd_profile,

        candidates,

        top_k=20
):

    candidate_text = (
        build_candidates(
            candidates
        )
    )
    
    prompt = f"""

        You are a senior recruiter.

        Job Description:

        {json.dumps(jd_profile)}

        Candidates:

        {candidate_text}

        Your task:

        Analyze all candidates.

        Rank them exactly as a human recruiter would.

        Consider:

        - technical skills
        - experience
        - leadership
        - domain expertise
        - seniority
        - architecture experience
        - project complexity

        Return ONLY JSON.

        Example:

        [
            {{
                "candidate_id":4,
                "rank":1,
                "reason":"Strong backend architecture experience"
            }}
        ]

        Return only top {top_k} candidates.
    """
    
    response = (client.chat.completions.create(
            model="qwen/qwen3-32b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        ))
    
    content = response.choices[0].message.content

    content = content.replace("```json", "").replace("```", "")

    return json.loads(content)[:top_k]
        