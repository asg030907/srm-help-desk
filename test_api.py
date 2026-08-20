"""
test_api.py
Tests for the FastAPI routes. The /chat test is skipped unless an LLM
API key is configured, since it would otherwise make a real model call;
/health is always exercised.
"""

import os

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="Requires a real LLM API key to exercise the agent end-to-end.",
)
def test_chat_endpoint_returns_response():
    response = client.post("/api/chat", json={"message": "What is 2 + 2?"})
    assert response.status_code == 200
    body = response.json()
    assert "session_id" in body
    assert "response" in body


def test_chat_endpoint_rejects_empty_message():
    response = client.post("/api/chat", json={"message": ""})
    assert response.status_code == 422


def test_tickets_endpoint_returns_list():
    """No LLM call needed — just reads the shared ticket store."""
    response = client.get("/api/tickets")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="Requires a real LLM API key to exercise the Dispatch Agent end-to-end.",
)
def test_dispatch_run_endpoint():
    response = client.post("/api/dispatch/run")
    assert response.status_code == 200
    assert "summary" in response.json()
