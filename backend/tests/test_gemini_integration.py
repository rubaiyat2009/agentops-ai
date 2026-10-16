import os
import pytest
pytest.importorskip("google.genai")
from unittest.mock import patch
from app.ai import analyze
from app.data import INCIDENTS, RUNBOOKS

class FakeResponse:
    text = '{"summary":"Admission check indicates quota exhaustion","probable_cause":"CPU quota full; OOM is separate","evidence":["cohort quota cpu 96/96 used"],"recommendations":["Inspect ClusterQueue"],"confidence":"high","runbook_ids":["RB-01"]}'

class FakeModels:
    def generate_content(self, **kwargs):
        assert 'diagnostics' in kwargs['contents']
        return FakeResponse()

class FakeClient:
    models = FakeModels()

def test_gemini_api_uses_diagnostics_and_no_firestore():
    with patch.dict(os.environ, {'AI_PROVIDER':'gemini-api','GEMINI_API_KEY':'test-key'}):
        with patch('google.genai.Client', return_value=FakeClient()) as client:
            result = analyze(INCIDENTS[0], RUNBOOKS)
    client.assert_called_once_with(api_key='test-key')
    assert result['mode'] == 'gemini-developer-api'
    assert result['diagnostics']['read_only'] is True
    assert result['model']
