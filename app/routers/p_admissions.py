from fastapi import APIRouter, status, HTTPException, Depends
from ..body import TokenData
from ..response import AdmissionResponse
from ..relationships import admission_relationship
from ..database import Database
from typing import List
from ..oauth2 import get_current_patient
from ..status_codes import validate_logged_in_user, validate_patient_exists, validate_patient_admissions

#admissions of patients (only get_all and get_by_id requests)
router = APIRouter(
    prefix="/patients/{patient_id}/admissions",
    tags=["Patient Admissions"]
)

db = Database()

@router.get("/", response_model=List[AdmissionResponse])
def get_admissions(patient_id: int, current_patient: TokenData = Depends(get_current_patient)):
    validate_logged_in_user(patient_id, current_patient.id)
    db.cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
    patient = db.cursor.fetchone()
    validate_patient_exists(patient, patient_id)

    db.cursor.execute("SELECT * FROM admissions WHERE patient_id = %s", (current_patient.id,))
    admissions = db.cursor.fetchall()
    validate_patient_admissions(admissions)

    relationship_response = []
    for admission in admissions:
        new_admission = admission_relationship(admission, db)
        relationship_response.append(AdmissionResponse(**new_admission))            #[AdmissionResponse(**row) for row in admissions] - before relationship implementation

    return relationship_response

@router.get("/{admission_id}", response_model=AdmissionResponse)
def get_admission_by_id(patient_id: int, admission_id: int, current_patient: TokenData = Depends(get_current_patient)):
    validate_logged_in_user(patient_id, current_patient.id)

    db.cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
    patient = db.cursor.fetchone()
    validate_patient_exists(patient, patient_id)
    
    db.cursor.execute("SELECT * FROM admissions WHERE id = %s AND patient_id = %s", (admission_id, current_patient.id))
    admission = db.cursor.fetchone()
    validate_patient_admissions(admission)

    relationship_response = admission_relationship(admission, db)
    
    return AdmissionResponse(**relationship_response)
