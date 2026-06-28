import os
import json

from openai import OpenAI
from dotenv import load_dotenv

from app.services.llm.prompts import (build_resume_prompt)

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv(
        "OPENROUTER_API_KEY"
    )
)

def parseResumeWithLlm(resumeText: str):
    
    print("============= RESUME PARSER STARTED ===============")
    
    prompt = build_resume_prompt(resumeText)
    
    response = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )
    
    content = response.choices[0].message.content
    content = content.replace("```json", "").replace("```", "")
    
    print("Resume response:-", json.loads(content))
    
    return json.loads(content)
    