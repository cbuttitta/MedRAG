from pydantic import BaseModel, field_validator


class PatientInput(BaseModel):
    """
    The request body for POST /api/recommend.
    raw_text is a freeform string containing the patient's lab values
    and visit notes pasted as plain text.
    """
    raw_text: str

    @field_validator('raw_text')
    @classmethod
    def must_not_be_empty(cls, v):
        """
        Validators run automatically when the model is instantiated.
        This one raises a ValueError if raw_text is blank or whitespace-only.
        Flask will catch this and return a 422 error automatically.
        """
        if not v or not v.strip():
            raise ValueError('raw_text cannot be empty')
        return v.strip()


class Recommendation(BaseModel):
    """
    A single recommendation returned by the LLM.
    Every field is required — if the LLM omits one, Pydantic raises an error.
    """
    category: str    # 'Diet', 'Exercise', 'Lifestyle', or 'Supplement'
    action: str      # The specific, actionable instruction
    rationale: str   # Why this applies to this particular patient
    sources: list[str]  # Which document sources support this recommendation


class RecommendationResponse(BaseModel):
    """
    The full response body returned by POST /api/recommend.
    """
    inferred_conditions: list[str]
    recommendations: list[Recommendation]
    disclaimer: str

