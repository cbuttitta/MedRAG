import pytest
from pydantic import ValidationError
from api.models.schemas import PatientInput, Recommendation

def test_patient_input_valid():
    """Valid input should parse without error."""
    p = PatientInput(raw_text='HbA1c: 7.9%, LDL: 142')
    assert p.raw_text == 'HbA1c: 7.9%, LDL: 142'

def test_patient_input_strips_whitespace():
    """Leading/trailing whitespace should be stripped by the validator."""
    p = PatientInput(raw_text='  some text  ')
    assert p.raw_text == 'some text'

def test_patient_input_empty_raises():
    """Empty string should raise ValidationError."""
    with pytest.raises(ValidationError):
        PatientInput(raw_text='')

def test_patient_input_whitespace_only_raises():
    """Whitespace-only string should raise ValidationError."""
    with pytest.raises(ValidationError):
        PatientInput(raw_text='   ')

def test_recommendation_valid():
    r = Recommendation(
        category='Diet',
        action='Reduce carbs',
        rationale='High HbA1c',
        sources=['ADA 2024']
    )
    assert r.category == 'Diet'

def test_recommendation_missing_field_raises():
    """Missing required field should raise ValidationError."""
    with pytest.raises(ValidationError):
        Recommendation(category='Diet', action='Reduce carbs')  # missing rationale, sources

