import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()


def extract_conditions(raw_text: str) -> list[str]:
    """
    First LLM call in the pipeline.
    Sends the raw patient text to GPT-4o-mini and extracts a list of
    medical conditions — both explicitly stated and inferred from biomarkers.

    Example input:
      'HbA1c: 7.9%, LDL: 142 mg/dL, fasting glucose: 168. Patient reports fatigue.'

    Example output:
      ['Type 2 Diabetes', 'Hyperlipidemia']
    """
    response = client.chat.completions.create(
        model='gpt-4o-mini',

        # response_format forces the model to return valid JSON.
        # Without this, the model might include prose like 'Here are the conditions:'
        # which would break json.loads().
        response_format={'type': 'json_object'},

        messages=[
            {
                'role': 'system',
                'content': '''You are a clinical NLP system.
Extract all medical conditions from the provided patient data.
Include conditions that are explicitly named AND conditions that can be
inferred from out-of-range biomarker values.
Return ONLY a JSON object in this exact format:
{"conditions": ["Condition One", "Condition Two"]}
Use standard medical terminology. Do not include normal findings.
If no conditions can be identified, return {"conditions": []}.'''
            },
            {
                'role': 'user',
                'content': raw_text
            }
        ]
    )

    # Parse the JSON string from the model's response
    content = response.choices[0].message.content
    data = json.loads(content)

    # Return just the list, defaulting to empty list if key is missing
    return data.get('conditions', [])

