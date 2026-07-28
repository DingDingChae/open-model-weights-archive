from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, AsyncIterator

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

APP_ROOT = Path(__file__).resolve().parents[1]
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
MODEL_ALIASES = {
    "qwen3.6-27b": "qwen3.6:27b-bf16",
    "gemma3-27b": "gemma3:27b-it-fp16",
}

app = FastAPI(
    title="Open Model Weights Ollama Gateway",
    version="0.1.0",
    description="Local-first aliasing proxy for Ollama's native and OpenAI-compatible APIs.",
)


def _language(request: Request) -> str:
    requested = request.headers.get("x-language-mode", "en").lower()
    return requested if requested in {"en", "yue", "bilingual"} else "en"


def _message(key: str, language: str) -> str:
    messages = {
        "ollama_unavailable": {
            "en": "Ollama is unavailable. Start Ollama and retry.",
            "yue": "Ollama 而家冇應機。開返 Ollama 再試，唔好俾條 llama 蛇王。",
        }
    }
    pair = messages[key]
    if language == "bilingual":
        return f"{pair['en']} / {pair['yue']}"
    return pair[language]


def _map_model(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    mapped = dict(payload)
    model = mapped.get("model")
    if isinstance(model, str):
        mapped["model"] = MODEL_ALIASES.get(model.lower(), model)
    return mapped


async def _request_ollama(
    request: Request, path: str, payload: dict[str, Any] | None = None
) -> httpx.Response:
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            return await client.request(
                request.method,
                f"{OLLAMA_URL}{path}",
                json=_map_model(payload) if payload is not None else None,
                headers={"accept": request.headers.get("accept", "application/json")},
            )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail=_message("ollama_unavailable", _language(request)),
        ) from exc


@app.get("/health")
async def health(request: Request) -> JSONResponse:
    response = await _request_ollama(request, "/api/version")
    return JSONResponse(
        {
            "status": "ok" if response.is_success else "degraded",
            "ollama_url": OLLAMA_URL,
            "ollama_status": response.status_code,
            "aliases": MODEL_ALIASES,
        },
        status_code=200 if response.is_success else 503,
    )


@app.get("/v1/models")
async def models(request: Request) -> JSONResponse:
    response = await _request_ollama(request, "/v1/models")
    if not response.is_success:
        return JSONResponse(response.json(), status_code=response.status_code)
    body = response.json()
    existing = {item.get("id") for item in body.get("data", [])}
    for alias, target in MODEL_ALIASES.items():
        if target in existing and alias not in existing:
            body["data"].append(
                {"id": alias, "object": "model", "created": 0, "owned_by": "local-alias"}
            )
    return JSONResponse(body)


async def _stream(response: httpx.Response) -> AsyncIterator[bytes]:
    async for chunk in response.aiter_bytes():
        yield chunk


async def _proxy_json(request: Request, path: str) -> JSONResponse | StreamingResponse:
    try:
        payload = await request.json()
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON.") from exc
    response = await _request_ollama(request, path, payload)
    content_type = response.headers.get("content-type", "application/json")
    return JSONResponse(
        response.json(),
        status_code=response.status_code,
        headers={"x-ollama-model": str(_map_model(payload).get("model", ""))},
    ) if "application/json" in content_type else StreamingResponse(
        _stream(response), status_code=response.status_code, media_type=content_type
    )


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    return await _proxy_json(request, "/v1/chat/completions")


@app.post("/v1/responses")
async def responses(request: Request):
    return await _proxy_json(request, "/v1/responses")


@app.post("/api/chat")
async def native_chat(request: Request):
    return await _proxy_json(request, "/api/chat")


@app.post("/api/generate")
async def native_generate(request: Request):
    return await _proxy_json(request, "/api/generate")
