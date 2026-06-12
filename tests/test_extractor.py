import json
from unittest.mock import patch, MagicMock
from api.services.extractor import extract_conditions

def make_mock_response(content_dict: dict):
    """
    Creates a mock object that mimics the structure of an OpenAI API response.
    The real response is: response.choices[0].message.content
    We recreate that structure with MagicMock.
    """
    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps(content_dict)
    return mock_response


def test_extract_returns_list():
    """extract_conditions should return a plain list of strings."""
    mock_resp = make_mock_response({'conditions': ['Type 2 Diabetes', 'Hyperlipidemia']})

    # patch replaces client.chat.completions.create with a mock
    # during the duration of the with block.
    with patch('api.services.extractor.client') as mock_client:
        mock_client.chat.completions.create.return_value = mock_resp
        result = extract_conditions('HbA1c 7.9%')

    assert result == ['Type 2 Diabetes', 'Hyperlipidemia']


def test_extract_empty_conditions():
    """Should return empty list if model finds no conditions."""
    mock_resp = make_mock_response({'conditions': []})

    with patch('api.services.extractor.client') as mock_client:
        mock_client.chat.completions.create.return_value = mock_resp
        result = extract_conditions('All values normal')

    assert result == []

