# AgentOps AI

**An AI-powered incident investigation and operations assistant**

Built by **AgentForge AI** for **AI Builder Cup 2026**  
Challenge: *Future of Work & Enterprise Productivity*

## Why we built AgentOps AI

When something goes wrong in a distributed system, engineers often need to check several places before they can understand what happened. They look at monitoring dashboards, application logs, workload statuses, infrastructure limits, and internal runbooks.

Finding the root cause can take longer than expected, especially when multiple symptoms appear at the same time.

We built **AgentOps AI** to explore how generative AI can make this investigation process faster and more structured.

Instead of replacing engineers or automatically changing infrastructure, AgentOps AI brings incident evidence into one place, uses Gemini to help interpret it, and presents recommended next steps for human review.

## What it does

AgentOps AI provides a simple workflow for investigating operational incidents:

1. **View incidents:** Explore simulated incidents involving distributed workloads, API performance, and data processing.
2. **Review evidence:** Examine worker statuses, resource utilization, error information, and other relevant telemetry.
3. **Investigate with Gemini:** Generate an AI-assisted explanation of the likely problem, supporting evidence, and suggested actions.
4. **Track investigations:** Store investigation records in Firestore for later review.
5. **Review remediation:** Approve or reject proposed actions before executing a simulated remediation.
6. **Maintain an audit trail:** Record the action workflow so decisions can be reviewed.

The prototype includes scenarios inspired by real operational challenges, including Kubernetes workload scheduling, resource quotas, worker failures, and data pipeline issues.

## Technology stack

| Component | Technology |
|---|---|
| Frontend | React, Vite |
| Backend | Python, FastAPI |
| Generative AI | Google Gemini Developer API |
| Database | Google Cloud Firestore |
| Frontend hosting | Firebase Hosting |
| Backend hosting | Google Cloud Run (planned) |
| Containerization | Docker |

### How it works

The React frontend communicates with a FastAPI backend that manages incidents, investigation requests, and simulated remediation workflows.

When a user requests an investigation, the backend prepares incident evidence and sends it to Gemini. The resulting explanation and recommendations are returned to the UI, while investigation records can be stored in Firestore.

For remediation, the application follows an approval-based workflow. Actions are simulated and recorded rather than applied to real infrastructure.

## Current project status

The prototype is functional in the local development environment.

- React frontend deployed to Firebase Hosting.
- FastAPI backend running locally.
- Gemini Developer API integration tested successfully.
- Firestore connectivity verified.
- Sample incidents available in Firestore.
- Simulated approval and remediation workflow implemented.
- Docker configuration prepared for Cloud Run deployment.

**Live frontend:** https://agentops-ai.web.app

The public frontend is available, but the backend has not yet been deployed to Cloud Run. As a result, live API-dependent features on the public site are not fully available yet.

We will update this section once the backend deployment and public end-to-end testing are complete.

## Project structure

```text
AgentOps_AI_Full_Prototype/
├── backend/
│   ├── app/
│   │   ├── main.py          # API routes and workflow
│   │   ├── ai.py            # Gemini integration
│   │   ├── store.py         # Firestore and local storage
│   │   └── data.py          # Sample incidents and runbooks
│   ├── tests/
│   ├── Dockerfile
│   ├── .dockerignore
│   └── requirements.txt
├── frontend/
│   └── src/                 # React application
├── scripts/                 # Deployment helpers
├── firebase.json
└── README.md
```

## Running the application locally

### 1. Start the backend

Open PowerShell in the project directory:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

For a local simulation without cloud credentials:

```powershell
$env:DEMO_MODE="true"
python -m uvicorn app.main:app --reload --port 8080
```

The backend will be available at:

- API health: http://localhost:8080/api/health
- API documentation: http://localhost:8080/docs

### 2. Start the frontend

Open another PowerShell terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

The local simulation uses sample incidents and deterministic investigation results. It does not require a Gemini API key.

### 3. Enable Gemini and Firestore locally

To use the working Gemini Developer API integration and Firestore, configure your credentials before starting the backend:

```powershell
$env:AI_PROVIDER="gemini-api"
$env:STORAGE_BACKEND="firestore"
$env:GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
$env:DEMO_MODE="false"

python -m uvicorn app.main:app --reload --port 8080
```

You also need valid Google Cloud Application Default Credentials with permission to access the Firestore database.

Do not commit API keys, credential files, or local environment settings to GitHub.

## Google Cloud deployment

The intended deployment uses Firebase Hosting for the frontend, Cloud Run for the FastAPI backend, and Firestore for persistent records.

### Backend

The backend includes a Dockerfile and can be deployed directly from its source directory using Google Cloud Build.

After enabling billing and the required Google Cloud APIs, configure the Cloud Run runtime service account, Firestore permissions, and Gemini API key securely.

Then deploy using Google Cloud CLI:

```powershell
cd backend

gcloud run deploy agentops-api `
  --source . `
  --project YOUR_PROJECT_ID `
  --region asia-southeast1 `
  --min-instances 0 `
  --max-instances 1
```

Before allowing public access, review the API's authentication, authorization, and simulated action endpoints.

The Gemini API key should be provided securely through Secret Manager rather than committed to the repository.

### Frontend

After the Cloud Run service is available, configure the frontend to use its public API URL, rebuild the React application, and deploy it to Firebase Hosting.

```powershell
cd frontend

npm install
npm run build

cd ..

firebase deploy --only hosting
```

The frontend API configuration and CORS settings must match the deployed Cloud Run URL and Firebase Hosting origin.

## Safety and limitations

**AgentOps AI is a hackathon prototype, not a production operations platform.**

All incidents, telemetry, and operational evidence are synthetic. Remediation actions are simulated and do not modify Kubernetes clusters, resource quotas, cloud services, or production environments.

Gemini-generated explanations are intended to support investigation, not replace engineering judgment. Recommendations should be checked against the available evidence before decisions are made.

The current prototype does not include the authentication, authorization, abuse protection, and operational controls required for a production deployment.

## Team

**AgentForge AI**  
AI Builder Cup 2026

## License

MIT — see [LICENSE](LICENSE).
