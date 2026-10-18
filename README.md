# AgentOps AI

**An AI-powered incident investigation and operations assistant**  
Built by **AgentForge AI** for **AI Builder Cup 2026**  
Challenge: **Future of Work & Enterprise Productivity**

**[Try the live prototype](https://agentops-ai.web.app)** · [Cloud Run API health](https://agentops-ai.web.app/api/health)

## Why we built it

Investigating an incident in a distributed system can mean jumping between dashboards, logs, workload statuses and runbooks. Even when the evidence is available, connecting the dots takes time.

AgentOps AI brings that information together. Engineers can review an incident, ask Gemini to investigate the evidence, and assess suggested next steps before taking action. Our goal is to support faster, more consistent decisions—not to replace engineering judgment.

## What you can try

- **Operations dashboard:** Explore three synthetic incidents covering Kubernetes/Kueue scheduling, API latency and ETL validation warnings.
- **Workload signals:** See pending, running, failed and passed worker counts alongside incident logs.
- **Gemini investigation:** Generate a probable cause, evidence-backed diagnostic findings and recommendations.
- **Firestore history:** Save investigation results and simulated action records for review.
- **Human approval workflow:** Create, review and execute *simulated* remediation actions.
- **Knowledge center:** Browse runbook information where records are available. The current deployed dataset may not contain runbooks.

For example, incident **INC-1042** shows 120 pending Kueue workloads, a CPU cohort quota at 96/96, and a separate OOMKilled worker. Gemini distinguishes the admission bottleneck from the worker's memory failure and recommends verification and human review before any change.

## Live architecture

```text
Browser
   |
   v
Firebase Hosting (React / Vite)
   |  /api/** Hosting rewrite
   v
Cloud Run (FastAPI, asia-southeast1)
   |                         |
   v                         v
Cloud Firestore         Gemini Developer API
(incidents, investigations, simulated actions)
```

| Component | Technology | How it is used |
| --- | --- | --- |
| Frontend | React + Vite | Dashboard and investigation workflow |
| Hosting | Firebase Hosting | Serves the web app and forwards `/api/**` to Cloud Run |
| Backend | Python + FastAPI | Incident APIs, Gemini requests and simulated approvals |
| Compute | Google Cloud Run | Runs the containerized API in Singapore |
| Database | Cloud Firestore | Persists incident and investigation records |
| AI | Google Gemini Developer API | Analyzes synthetic incident evidence and suggests next steps |
| Secrets | Google Cloud Secret Manager | Supplies the Gemini API key to Cloud Run |
| Container | Docker | Packages the backend for deployment via Cloud Build |

**Live frontend:** https://agentops-ai.web.app  
**Cloud Run service:** https://agentops-api-751520950948.asia-southeast1.run.app  
**API health through Hosting:** https://agentops-ai.web.app/api/health  
**Sample incident API:** https://agentops-ai.web.app/api/incidents

The live deployment has been verified with three incidents, a successful Gemini investigation, and an investigation document persisted to Firestore. All telemetry is synthetic.

## Repository layout

```text
backend/app/main.py       FastAPI routes and approval workflow
backend/app/ai.py         Gemini Developer API integration
backend/app/store.py      Firestore and local demo storage
backend/app/data.py       Synthetic incident and runbook data
backend/app/diagnostics.py  Evidence-oriented diagnostics
backend/tests/            Backend tests
backend/Dockerfile        Cloud Run container definition
frontend/src/             React UI
firebase.json             Firebase Hosting and Cloud Run rewrites
scripts/                  Deployment helpers
```

## Run locally

Requires Python 3.11+, Node.js and npm. From the repository root, open PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DEMO_MODE="true"
python -m uvicorn app.main:app --reload --port 8080
```

In another PowerShell terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Local demo mode uses synthetic data and deterministic investigation responses; **it does not call Gemini**.

To use Gemini and Firestore locally, authenticate with Google Cloud Application Default Credentials and start the backend with:

```powershell
$env:DEMO_MODE="false"
$env:AI_PROVIDER="gemini-api"
$env:STORAGE_BACKEND="firestore"
$env:GOOGLE_CLOUD_PROJECT="agentops-ai"
$env:GEMINI_API_KEY="YOUR_OWN_GEMINI_API_KEY"
$env:GEMINI_MODELS="gemini-3.5-flash-lite"
python -m uvicorn app.main:app --reload --port 8080
```

Do not commit credentials or API keys. In local development, `frontend/.env` may point to `http://localhost:8080`. For production, set `VITE_API_URL=` in `frontend/.env.production` so requests use the same-origin Firebase Hosting `/api/**` rewrite.

## Cloud deployment

The working deployment uses Google Cloud project `agentops-ai`, region `asia-southeast1`, and Cloud Run service `agentops-api`.

1. Enable billing and the Cloud Run, Cloud Build, Artifact Registry, Firestore, IAM and Secret Manager APIs.
2. Create a runtime service account and grant it `roles/datastore.user` for Firestore.
3. Store the Gemini Developer API key in Secret Manager and grant the runtime service account secret access.
4. Deploy the backend from `backend/`:

```powershell
$PROJECT_ID="agentops-ai"
$REGION="asia-southeast1"
$SA="agentops-runtime@agentops-ai.iam.gserviceaccount.com"

gcloud run deploy agentops-api `
  --source . `
  --project $PROJECT_ID `
  --region $REGION `
  --service-account $SA `
  --set-env-vars "AI_PROVIDER=gemini-api,STORAGE_BACKEND=firestore,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DEMO_MODE=false,GEMINI_MODELS=gemini-3.5-flash-lite" `
  --set-secrets "GEMINI_API_KEY=agentops-gemini-key:1" `
  --min-instances 0 `
  --max-instances 1 `
  --memory 512Mi
```

5. Configure `firebase.json` with an `/api/**` rewrite to the Cloud Run service before the SPA `**` rewrite. Build the frontend with a blank `VITE_API_URL`, then run `firebase deploy --only hosting`.

**Public-access caution:** The hackathon deployment currently allows unauthenticated Cloud Run requests. This is appropriate only for a limited synthetic-data demonstration with controlled usage. Before production use, add Firebase Authentication, authorization, rate limits, abuse prevention, monitoring and cost controls. A billing budget alert is not a hard spending cap.

## Safety and limitations

This is a **hackathon prototype**, not a production operations control plane. It does not connect to a live Kubernetes cluster or execute real remediation. All telemetry, logs and incidents are synthetic, and the approval/action workflow is simulated. Gemini responses can be wrong and must be verified against evidence. No production quotas, workloads or external services are changed.

## Team and license

**AgentForge AI** · AI Builder Cup 2026  
MIT — see [LICENSE](LICENSE).
