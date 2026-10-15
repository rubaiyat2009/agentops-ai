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


def test_kueue_diagnostics():
 response=client.get('/api/incidents/INC-1042/diagnostics')
 assert response.status_code==200
 data=response.json()
 assert data['confidence']=='high'
 assert data['read_only'] is True
 assert {f['category'] for f in data['findings']} >= {'admission','execution'}
 assert 'quota' in data['probable_cause'].lower()

def test_unknown_incident():
 assert client.get('/api/incidents/UNKNOWN/diagnostics').status_code==404

def test_missing_evidence_is_not_invented():
 from app.diagnostics import diagnose
 result=diagnose({'metrics': {'pending': 4}, 'logs': []})
 assert result['confidence']=='low'
 assert 'quota exhaustion' not in result['probable_cause'].lower()
