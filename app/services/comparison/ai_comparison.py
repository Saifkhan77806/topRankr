import os
import json

from openai import OpenAI


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv(
        "OPENROUTER_API_KEY"
    )
)


def ai_compare_candidates(
        jd,
        candidates
):

    candidate_text = ""

    for candidate in candidates:

        candidate_text += f"""

Candidate ID:
{candidate["candidate_id"]}

Name:
{candidate["name"]}

Experience:
{candidate["experience"]}

Industry:
{candidate["industry"]}

Seniority:
{candidate["seniority"]}

Skills:
{candidate["skills"]}

Leadership:
{candidate["leadership"]}

Semantic Score:
{candidate["semantic_score"]}

Ranking Score:
{candidate["ranking_score"]}

AI Reason:
{candidate["ai_reason"]}

"""

    prompt = f"""

You are an expert recruiter.

JOB:

{json.dumps(jd)}

CANDIDATES:

{candidate_text}

Compare candidates.

Determine:

1. best candidate
2. strengths
3. weaknesses
4. hiring recommendation

Return JSON only.

Example:

{{
    "winner":4,
    "reason":
        "Candidate 4 has stronger backend architecture experience."
}}
"""

    response = (
        client.chat.completions.create(

            model="qwen/qwen3-32b",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0
        )
    )

    content = (
        response
        .choices[0]
        .message
        .content
    )

    content = (
        content
        .replace(
            "```json",
            ""
        )
        .replace(
            "```",
            ""
        )
    )

    return json.loads(
        content
    )