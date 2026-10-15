import os
os.environ['DEMO_MODE']='true'
from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_workflow():
 assert client.get('/api/health').json()['ok']
 incidents=client.get('/api/incidents').json();assert len(incidents)>=3
 i=incidents[0]['id']
 inv=client.post(f'/api/incidents/{i}/investigate').json();assert inv['mode']=='demo-simulated'
 action=client.post('/api/actions',json={'incident_id':i,'investigation_id':inv['id']}).json()
 assert client.post(f"/api/actions/{action['id']}/execute").status_code==409
 assert client.post(f"/api/actions/{action['id']}/approve").json()['status']=='approved'
 assert client.post(f"/api/actions/{action['id']}/execute").json()['status']=='simulated-complete'
