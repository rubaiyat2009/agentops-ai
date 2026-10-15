# AgentOps AI — AgentForge AI

**AI Builder Cup 2026 · Future of Work & Enterprise Productivity**

A functional prototype for investigating simulated enterprise incidents with Gemini on Vertex AI, tracking cases and approvals in Firestore, running an API on Cloud Run, and serving the UI from Firebase Hosting.

> **Safety:** All telemetry is synthetic. The action workflow is a simulation and **never** modifies Kubernetes, production quotas, or external services. This is a hackathon prototype, not a production-ready operations control plane.

## Features
- Incident dashboard with pending/running/failed/passed worker counts
- Synthetic incident logs and runbook knowledge center
- Gemini-based grounded incident investigation and recommendations
- Investigation records saved to Firestore
- Approval-required simulated remediation workflow and audit records
- React/Vite frontend deployed to Firebase Hosting; FastAPI backend deployed to Cloud Run

## Project structure
```
backend/app/main.py       API routes, approval workflow
backend/app/ai.py         Gemini on Vertex AI integration
backend/app/store.py      Firestore persistence or local demo store
backend/app/data.py       Synthetic sample incidents and runbooks
backend/tests/            Backend integration test
backend/Dockerfile        Cloud Run container
frontend/src/             React UI
firebase.json             Firebase Hosting configuration
scripts/                  Deployment helpers
```

## Local demo (no cloud credentials)
Terminal 1:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt httpx pytest
DEMO_MODE=true uvicorn app.main:app --reload --port 8080
```
Terminal 2:
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```
Open http://localhost:5173. The UI displays **DEMO SIMULATION** and returns deterministic analysis, **not Gemini output**. Demo storage is in-memory and resets on restart. Use the Google Cloud instructions below for the competition submission.

## Google Cloud deployment (real Gemini + Firestore)
Prerequisites: Google Cloud project with billing enabled; Firebase project linked to the **same** Google Cloud project; `gcloud`, Node.js 20+, npm, Firebase CLI (`npm install -g firebase-tools`), and permissions to enable APIs, deploy Cloud Run, create service accounts and manage Firestore. Use a supported region and confirm Vertex AI model availability. Google Cloud usage may incur costs.

1. Set variables, authenticate, and enable services:
```bash
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export SERVICE="agentops-api"
gcloud auth login
gcloud config set project "$PROJECT_ID"
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com aiplatform.googleapis.com firestore.googleapis.com iam.googleapis.com
```
2. Create a **Firestore Native mode** database named `(default)` from Firebase console > Build > Firestore Database (choose a supported location). Firebase Hosting also must be enabled for the same project.
3. Create a least-privilege runtime service account:
```bash
gcloud iam service-accounts create agentops-runtime --display-name="AgentOps Cloud Run runtime"
export RUNTIME_SA="agentops-runtime@${PROJECT_ID}.iam.gserviceaccount.com"
gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:${RUNTIME_SA}" --role="roles/datastore.user"
gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:${RUNTIME_SA}" --role="roles/aiplatform.user"
```
4. Deploy the backend from the repo root. First prepare the environment file and replace placeholders:
```bash
cp scripts/env.example.yaml scripts/env.yaml
# Edit scripts/env.yaml: replace YOUR_PROJECT_ID with the real project ID
export PROJECT_ID="your-project-id"
export REGION="us-central1"
bash scripts/deploy-backend.sh
```
The script uses `--env-vars-file` so the comma-separated CORS origins are passed correctly.

5. Deploy frontend with the Cloud Run URL (replace placeholder with output from `gcloud run services describe`):
```bash
export API_URL="$(gcloud run services describe "$SERVICE" --region "$REGION" --format='value(status.url)')"
cd frontend
printf 'VITE_API_URL=%s\n' "$API_URL" > .env.production
npm install
npm run build
cd ..
firebase login
firebase use --add "$PROJECT_ID"
firebase deploy --only hosting
```
6. In the Google Cloud Console, update Cloud Run environment `ALLOWED_ORIGINS` to your exact Firebase Hosting URL(s) if different. Verify `https://YOUR_PROJECT.web.app`, backend `/api/health`, Gemini investigation, Firestore `investigations` and `actions` collections, and approval simulation end to end.

**Production caution:** This hackathon app uses public, unauthenticated endpoints and sample data. Do not store real operational secrets or confidential logs. For production, add Firebase Authentication, per-user authorization, API rate limiting, abuse protection, monitoring, and bounded billing. Keep Cloud Run max instances and budgets low for demo purposes. Gemini responses can be inaccurate; always verify evidence.

## Demo / submission checklist
- [ ] Public Firebase Hosting URL works in private browser
- [ ] Cloud Run API health and Gemini investigation work
- [ ] Firestore records are persisted (verify Console)
- [ ] Approve then execute a **simulated** action; unapproved execution returns 409
- [ ] Public GitHub repository includes code and setup steps, but no credentials
- [ ] 3–4 minute demo shows actual UI and the complete workflow
- [ ] Fill official competition pitch deck template, including screenshots and URLs

## Troubleshooting
- 503 from investigation: verify Vertex AI API enabled, model access/region, runtime service account role and billing. See Cloud Run logs.
- 500 on Firestore access: create the `(default)` Firestore database and grant runtime SA `roles/datastore.user`.
- Browser CORS: set `ALLOWED_ORIGINS` to the exact Firebase Hosting origin, no trailing slash.
- Missing data: ensure `AUTO_SEED=true` for first deployment; it inserts only missing sample documents.
- Public API URL: `/docs` is accessible and can be used for endpoint inspection. Do not expose confidential data.

## License
MIT (see LICENSE).
