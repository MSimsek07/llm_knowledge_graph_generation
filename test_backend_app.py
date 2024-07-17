import os
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from pydantic import BaseModel
from unittest.mock import patch
from langchain_core.documents import Document
from backend2 import app, load_env_variables, make_research, generate_research_report, create_document

class ResearchInput(BaseModel):
    input_text: str

client = TestClient(app)

@pytest.fixture
def mock_env_vars():
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test", "LANGCHAIN_API_KEY": "test", "NEO4J_URI": "neo4j+s://test", "NEO4J_USERNAME": "neo4j", "NEO4J_PASSWORD": "test"}):
        yield


def test_make_research():
    input_text = "test research"
    with patch("backend2.GoogleScholarQueryRun.run", return_value="test response"):
        response = make_research(input_text)
        assert response == "<p>test response</p>"

def test_generate_research_report():
    response = "test response"
    with patch("backend2.LLMChain.run", return_value="test report"):
        report = generate_research_report(response)
        assert report == "test report"

def test_create_document():
    text = "test document"
    documents = create_document(text)
    assert len(documents) == 1
    assert documents[0].page_content == text

def test_create_document_empty_text():
    with pytest.raises(ValueError, match="Text cannot be empty"):
        create_document("")

def test_generate_graph_success(mock_env_vars):
    input_data = {"input_text": "test input"}
    with patch("backend2.make_research", return_value="test research response"):
        with patch("backend2.generate_research_report", return_value="test research report"):
            with patch("backend2.create_document", return_value=[Document(page_content="test document")]):
                with patch("backend2.convert_to_graph_documents", return_value=["test graph document"]):
                    with patch("backend2.add_graph_documents") as mock_add_graph_documents:
                        with patch("backend2.clear_graph_db") as mock_clear_graph_db:
                            response = client.post("/generate_graph", json=input_data)
                            assert response.status_code == 200
                            data = response.json()
                            assert data["research_response"] == "test research response"
                            assert data["research_report"] == "test research report"
                            assert data["documents"] == ["test document"]
                            assert data["graph_documents"] == ["test graph document"]
                            mock_add_graph_documents.assert_called_once()
                            mock_clear_graph_db.assert_called_once()

def test_generate_graph_failure(mock_env_vars):
    input_data = {"input_text": "test input"}
    with patch("backend2.load_env_variables", side_effect=ValueError("Environment variable missing")):
        response = client.post("/generate_graph", json=input_data)
        assert response.status_code == 500
        assert response.json()["detail"] == "Environment variable missing"
