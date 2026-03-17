from fastapi.testclient import TestClient

from backend.app import app
from backend.store import clear_latest_target_name


client = TestClient(app)


def setup_function() -> None:
    clear_latest_target_name()


def test_status_is_empty_before_generation() -> None:
    response = client.get("/status")

    assert response.status_code == 200
    assert response.json() == {"target_name": None}


def test_verify_requires_generated_target() -> None:
    response = client.post("/verify", json={"candidate": "Alice Smith"})

    assert response.status_code == 409
    assert "No target name generated yet" in response.json()["detail"]


def test_generate_updates_latest_target() -> None:
    response = client.post(
        "/generate",
        json={"prompt": "Generate a western full name"},
    )

    assert response.status_code == 200
    generated_name = response.json()["name"]
    assert isinstance(generated_name, str)
    assert generated_name

    status_response = client.get("/status")
    assert status_response.status_code == 200
    assert status_response.json() == {"target_name": generated_name}


def test_verify_returns_structured_result_after_generation() -> None:
    generate_response = client.post(
        "/generate",
        json={"prompt": "Generate a western full name"},
    )
    generated_name = generate_response.json()["name"]

    response = client.post("/verify", json={"candidate": generated_name})

    assert response.status_code == 200
    body = response.json()
    assert body["match"] is True
    assert body["confidence"] == 1.0
    assert body["reason"] == "Exact match"
