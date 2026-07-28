# Open Model Weights Archive

Pinned, verifiable archives of two complete 27B models, stored as public OCI artifacts
in GitHub Container Registry (GHCR) rather than metered Git LFS:

| Friendly ID | Upstream snapshot | Ollama runtime |
| --- | --- | --- |
| `qwen3.6-27b` | `qwen3.6:27b-bf16` | BF16, 56 GB |
| `gemma3-27b` | `gemma3:27b-it-fp16` | FP16, 55 GB |

These are full-parameter, non-pruned 27B models. Lower-bit runtime variants are
not used for the archive.

## API

The API is a small, local-first gateway to Ollama. It exposes:

- `GET /health`
- `GET /v1/models`
- `POST /v1/chat/completions`
- `POST /v1/responses`
- `POST /api/chat`
- `POST /api/generate`

Start it:

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8080
```

Pull the local Qwen runtimes:

```powershell
ollama pull qwen3.6:27b-bf16
ollama pull gemma3:27b-it-fp16
```

```powershell
curl.exe http://127.0.0.1:8080/v1/chat/completions `
  -H "Content-Type: application/json" `
  -d '{"model":"qwen3.6-27b","messages":[{"role":"user","content":"Hello"}]}'
```

Configuration is described in [API documentation](docs/api/README.md).

## Archive

`models.lock.json` pins each Ollama manifest digest and its expected download
size. `scripts/archive-models.ps1` pulls each complete model and publishes its
manifest and referenced blobs as an OCI artifact. Git tracks verified CheapLFS
pointers; model bytes never enter ordinary Git history.

See [model storage](docs/storage/README.md), [roadmap](ROADMAP.md), and
[handoff](HANDOFF.md).

## License

The code in this repository is MIT licensed. Model weights retain their
upstream licenses; consult each upstream model card before use or redistribution.
