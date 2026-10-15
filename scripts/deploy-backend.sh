#!/usr/bin/env bash
set -euo pipefail
: "${PROJECT_ID:?Set PROJECT_ID}"
REGION="${REGION:-us-central1}"
SERVICE="${SERVICE:-agentops-api}"
RUNTIME_SA="agentops-runtime@${PROJECT_ID}.iam.gserviceaccount.com"
if [[ ! -f scripts/env.yaml ]]; then echo "Copy scripts/env.example.yaml to scripts/env.yaml and replace YOUR_PROJECT_ID";exit 1;fi
gcloud run deploy "$SERVICE" --source backend --project "$PROJECT_ID" --region "$REGION" --allow-unauthenticated --service-account "$RUNTIME_SA" --env-vars-file scripts/env.yaml --max-instances 3
