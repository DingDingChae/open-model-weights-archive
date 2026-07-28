from fastapi.testclient import TestClient

from app import main


def test_model_aliases_are_full_precision() -> None:
    assert main.MODEL_ALIASES == {
        "qwen3.6-27b": "qwen3.6:27b-bf16",
        "gemma3-27b": "gemma3:27b-it-fp16",
    }


def test_invalid_json_is_rejected() -> None:
    client = TestClient(main.app)
    response = client.post(
        "/v1/chat/completions",
        content="{",
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Request body must be valid JSON."


def test_language_mode_falls_back_to_english() -> None:
    client = TestClient(main.app)
    request = client.build_request("GET", "/health", headers={"x-language-mode": "xx"})
    assert main._language(request) == "en"
