from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()

# Authentication setup
security = HTTPBasic()

def authenticate(credentials: HTTPBasicCredentials):
    if credentials.username != "admin" or credentials.password != "password":
        raise HTTPException(status_code=401, detail="Invalid credentials")

# Patient model
class Patient(BaseModel):
    id: int
    name: str = Field(..., min_length=1)
    age: int = Field(..., ge=0)
    condition: Optional[str] = None

# In-memory database
patients_db = {}

# Add a new patient
@app.post("/patients/", status_code=201)
def add_patient(patient: Patient, credentials: HTTPBasicCredentials = Depends(security)):
    authenticate(credentials)
    if patient.id in patients_db:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists")
    patients_db[patient.id] = patient
    return {"message": "Patient added successfully", "patient": patient}

# Retrieve a patient by ID
@app.get("/patients/{patient_id}", response_model=Patient)
def get_patient(patient_id: int, credentials: HTTPBasicCredentials = Depends(security)):
    authenticate(credentials)
    patient = patients_db.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

# Update an existing patient
@app.put("/patients/{patient_id}")
def update_patient(patient_id: int, updated_patient: Patient, credentials: HTTPBasicCredentials = Depends(security)):
    authenticate(credentials)
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    patients_db[patient_id] = updated_patient
    return {"message": "Patient updated successfully", "patient": updated_patient}

# List all patients
@app.get("/patients/", response_model=List[Patient])
def list_patients(credentials: HTTPBasicCredentials = Depends(security)):
    authenticate(credentials)
    return list(patients_db.values())
