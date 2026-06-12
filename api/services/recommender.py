import json
from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = '''You are a clinical decision support tool.
Your job is to generate specific, actionable recommendations for a patient
based on their medical data and the provided medical literature.

STRICT RULES:
1. Only recommend actions supported by the provided medical literature context.
2. Do not invent recommendations not mentioned in the context.
3. Do not recommend specific prescription medications.
   You MAY note medication classes a doctor may consider (e.g. 'a doctor may
   consider statin therapy') but never recommend a patient take a specific drug.
4. Every recommendation must cite at least one source from the context.
5. Return ONLY valid JSON — no preamble, no explanation, no markdown.

Return a JSON object matching this exact schema:
{
  "recommendations": [
    {
      "category": "Diet" | "Exercise" | "Lifestyle" | "Supplement",
      "action": "specific instruction the patient can act on today",
      "rationale": "why this applies to this patient based on their data",
      "sources": ["Source Name"]
    }
  ]
}

Aim for 4-8 total recommendations spread across relevant categories.
Make actions specific: not 'eat healthy' but 'reduce refined carbohydrate
intake to below 130g per day and prioritize low-glycemic foods such as
legumes, non-starchy vegetables, and whole grains.'''


def generate_recommendations(
    conditions: list[str],
    retrieved_chunks: list[dict],
    raw_text: str
) -> dict:
    """
    Second LLM call in the pipeline.
    Builds an augmented prompt containing:
      1. The patient's original data
      2. Inferred conditions
      3. Retrieved medical literature chunks
    Then asks GPT-4o-mini to generate structured recommendations.
    """

    # Format the retrieved chunks as a readable context block.
    # Each chunk is labeled with its source so the model can cite it.
    context_parts = []
    for chunk in retrieved_chunks:
        label = f'[{chunk["source"]}]'
        if chunk.get('section'):
            label = f'[{chunk["source"]} — {chunk["section"]}]'
        context_parts.append(f'{label}\n{chunk["content"]}')
    context = '\n\n'.join(context_parts)

    # Build the full user message combining all inputs
    user_message = f'''PATIENT DATA:
{raw_text}

INFERRED CONDITIONS:
{', '.join(conditions)}

RELEVANT MEDICAL LITERATURE:
{context}

Generate structured recommendations for this patient
using only the literature provided above.'''

    response = client.chat.completions.create(
        model='gpt-4o-mini',
        response_format={'type': 'json_object'},
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user',   'content': user_message}
        ]
    )

    content = response.choices[0].message.content
    return json.loads(content)

