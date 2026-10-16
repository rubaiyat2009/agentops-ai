# Gemini Developer API (no Google Cloud billing required for eligible free-tier use)

## Local Windows PowerShell

```powershell
cd C:\Document\AI_Builder_Cup\AgentOps_AI_Full_Prototype\backend
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:AI_PROVIDER="gemini-api"
$env:STORAGE_BACKEND="memory"
$env:GEMINI_API_KEY="YOUR_PRIVATE_KEY"
$env:GEMINI_MODELS="gemini-3.5-flash-lite,gemini-3.1-flash-lite"
python -m uvicorn app.main:app --reload --port 8080
```

In a separate terminal run the frontend as before (`npm run dev`).
Visit http://localhost:8080/api/health and verify `mode=gemini-api` and `storage=memory`.
Click **Investigate with Gemini** and verify the result mode `gemini-developer-api`.
The Gemini request includes incident, deterministic diagnostics, and runbooks.

For offline demo use `AI_PROVIDER=demo` (keep `STORAGE_BACKEND=memory`).
Firestore later: `STORAGE_BACKEND=firestore` (requires Firestore project and credentials).
Vertex AI later: `AI_PROVIDER=vertex-ai` (requires GCP project and authentication).

## Safety

This is a synthetic-data prototype. No real Kubernetes mutations are made.
The approve/execute endpoints simulate approvals; they are NOT authenticated.
Do not expose this backend publicly with write endpoints until authentication,
authorization, rate limits, and abuse controls are implemented.

Never commit `.env`, share a ZIP containing credentials, or expose API keys in Vite.
If a key was exposed, revoke and replace it in Google AI Studio.
