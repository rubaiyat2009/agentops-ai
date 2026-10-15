import os,uuid
from datetime import datetime,timezone
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field
from .store import store
from .ai import analyze
from .diagnostics import diagnose

app=FastAPI(title="AgentOps AI API",version="1.0.0")
origins=[x.strip() for x in os.getenv('ALLOWED_ORIGINS','http://localhost:5173').split(',') if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_methods=['GET','POST'],allow_headers=['Content-Type'])

def now():return datetime.now(timezone.utc).isoformat()
@app.on_event('startup')
def startup():
 if os.getenv('AUTO_SEED','false').lower()=='true':store.seed()
@app.get('/api/health')
def health():return {'ok':True,'mode':'demo-simulated' if store.demo else 'google-cloud'}
@app.get('/api/incidents')
def incidents():return sorted(store.list('incidents'),key=lambda x:x['id'])
@app.get('/api/incidents/{incident_id}')
def incident(incident_id:str):
 value=store.get('incidents',incident_id)
 if not value:raise HTTPException(404,'Incident not found')
 return value
@app.get('/api/incidents/{incident_id}/diagnostics')
def incident_diagnostics(incident_id:str):
 item=store.get('incidents',incident_id)
 if not item:raise HTTPException(404,'Incident not found')
 return diagnose(item)
@app.get('/api/runbooks')
def runbooks():return store.list('runbooks')
@app.post('/api/incidents/{incident_id}/investigate')
def investigate(incident_id:str):
 item=store.get('incidents',incident_id)
 if not item:raise HTTPException(404,'Incident not found')
 books=store.list('runbooks')
 try:result=analyze(item,books)
 except Exception as exc:
  raise HTTPException(503,'AI service unavailable; retry later') from exc
 record={'id':str(uuid.uuid4()),'incident_id':incident_id,'created':now(),**result}
 store.put('investigations',record['id'],record)
 return record
class ActionRequest(BaseModel):
 incident_id:str=Field(min_length=1,max_length=64)
 investigation_id:str=Field(min_length=1,max_length=64)
 note:str=Field(default='',max_length=300)
@app.post('/api/actions')
def create_action(req:ActionRequest):
 inv=store.get('investigations',req.investigation_id)
 if not inv or inv['incident_id']!=req.incident_id:raise HTTPException(400,'Investigation not found for incident')
 item={'id':str(uuid.uuid4()),'incident_id':req.incident_id,'investigation_id':req.investigation_id,'type':'simulated-quota-review','note':req.note,'status':'pending-approval','created':now()}
 store.put('actions',item['id'],item)
 return item
@app.post('/api/actions/{action_id}/approve')
def approve(action_id:str):
 item=store.get('actions',action_id)
 if not item:raise HTTPException(404,'Action not found')
 if item['status']!='pending-approval':raise HTTPException(409,'Action already processed')
 item.update(status='approved',approved_at=now());store.put('actions',action_id,item)
 return item
@app.post('/api/actions/{action_id}/execute')
def execute(action_id:str):
 item=store.get('actions',action_id)
 if not item:raise HTTPException(404,'Action not found')
 if item['status']!='approved':raise HTTPException(409,'Approval required')
 item.update(status='simulated-complete',executed_at=now(),result='Simulation only: no production workloads or quotas were modified.')
 store.put('actions',action_id,item)
 return item
@app.get('/api/actions')
def actions():return store.list('actions')
