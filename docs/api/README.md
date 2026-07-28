# Ollama API

## Behavior

The gateway maps friendly archive IDs to Ollama tags and forwards JSON requests
to `OLLAMA_URL` (default `http://127.0.0.1:11434`). Both Ollama-native and
OpenAI-compatible calls are supported.

## Configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `OLLAMA_URL` | `http://127.0.0.1:11434` | Trusted Ollama service URL |

Bind the gateway to loopback unless you add authentication and TLS at a trusted
reverse proxy.

## Failure modes

- Ollama unreachable: HTTP 503 with an English, Cantonese, or bilingual message.
- Model absent: Ollama's original response is returned.
- Invalid JSON: HTTP 400.

## Language

Set `X-Language-Mode` to `en`, `yue`, or `bilingual`. Language affects gateway
messages, not model output. Facts are unchanged by the playful Cantonese copy.

## Verification

Run `pytest`. Integration tests use a disposable mock Ollama server and do not
send prompts to an external service.
