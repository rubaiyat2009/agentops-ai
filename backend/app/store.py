import os
from copy import deepcopy
from threading import Lock
from .data import INCIDENTS, RUNBOOKS

class Store:
 def __init__(self):
  self.lock=Lock()
  self.demo=os.getenv("DEMO_MODE","false").lower()=="true"
  self.db=None
  if not self.demo:
   from google.cloud import firestore
   self.db=firestore.Client()
  self.memory={"incidents":{x["id"]:deepcopy(x) for x in INCIDENTS},"runbooks":{x["id"]:deepcopy(x) for x in RUNBOOKS},"investigations":{},"actions":{}}
 def seed(self):
  if self.demo:return
  for collection,records in [("incidents",INCIDENTS),("runbooks",RUNBOOKS)]:
   for item in records:
    ref=self.db.collection(collection).document(item["id"])
    if not ref.get().exists:ref.set(item)
 def list(self,col):
  if self.demo:
   with self.lock:return deepcopy(list(self.memory[col].values()))
  return [dict(s.to_dict(),id=s.id) for s in self.db.collection(col).stream()]
 def get(self,col,id):
  if self.demo:
   with self.lock:return deepcopy(self.memory[col].get(id))
  snap=self.db.collection(col).document(id).get()
  return dict(snap.to_dict(),id=snap.id) if snap.exists else None
 def put(self,col,id,item):
  if self.demo:
   with self.lock:self.memory[col][id]=deepcopy(item)
  else:self.db.collection(col).document(id).set(item)
store=Store()
