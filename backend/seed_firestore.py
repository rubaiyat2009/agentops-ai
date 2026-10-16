import os
import requests
from google.cloud import firestore

project_id = os.environ["GOOGLE_CLOUD_PROJECT"]

response = requests.get(
    "http://127.0.0.1:8080/api/incidents",
    timeout=15
)
response.raise_for_status()

incidents = response.json()

if not isinstance(incidents, list) or not incidents:
    raise RuntimeError("No demo incidents found. Seeding stopped.")

db = firestore.Client(project=project_id)

for incident in incidents:
    incident_id = incident.get("id")

    if not incident_id:
        raise ValueError(f"Incident missing ID: {incident}")

    db.collection("incidents").document(
        str(incident_id)
    ).set(incident)

    print(f"Saved {incident_id}")

print(f"Successfully seeded {len(incidents)} incidents.")