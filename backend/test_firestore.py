import os
from google.cloud import firestore

project_id = os.environ["GOOGLE_CLOUD_PROJECT"]

db = firestore.Client(project=project_id)

doc_ref = db.collection("connection_tests").document("local_test")

doc_ref.set({
    "application": "AgentOps AI",
    "status": "connected",
    "source": "local-fastapi"
})

print("Firestore write successful!")
print(doc_ref.get().to_dict())