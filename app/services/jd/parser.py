import json

from app.services.llm.openrouter_service import ( client )

from app.services.jd.prompts import ( build_jd_prompt )


def parse_job_description( job_description: str ):

    prompt = build_jd_prompt(job_description)

    response = (
        client.chat.completions.create(
            model="qwen/qwen3-32b",
            messages=[
                {
                    "role":"user",
                    "content":prompt
                }
            ],
            temperature=0
        )
    )

    content = response.choices[0].message.content
    

    content = content.replace("```json", "").replace("```", "").strip()
    

    return json.loads(content)