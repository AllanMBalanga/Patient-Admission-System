from fastapi import status, APIRouter, HTTPException, Depends
from ..database import Database
from ..body import DoctorToken, PatientToken
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from ..utils import verify
from ..oauth2 import create_token

#/login/patients and login/doctors (post requests only)
router = APIRouter(
    prefix="/login",
    tags=["Login"]
)

db = Database()

@router.post("/patients", response_model=PatientToken)
def patient_login(credentials: OAuth2PasswordRequestForm = Depends()):
    db.cursor.execute("SELECT * FROM patients WHERE email = %s", (credentials.username,))
    patient = db.cursor.fetchone()

    if not patient:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid credentials.")
    
    if not verify(credentials.password, patient["password"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid credentials.")
    
    access_token = create_token(data={"user_id": patient["id"]})

    return {"access_token": access_token, "token_type": "bearer", "patient_id": patient["id"]}

@router.post("/doctors", response_model=DoctorToken)
def doctor_login(credentials: OAuth2PasswordRequestForm = Depends()):
    db.cursor.execute("SELECT * FROM doctors WHERE email = %s", (credentials.username,))
    doctor = db.cursor.fetchone()
    
    if not doctor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid credentials.")
    
    if not verify(credentials.password, doctor["password"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid credentials.")

    access_token = create_token(data={"user_id": doctor["id"]})

    return {"access_token": access_token, "token_type": "bearer", "doctor_id": doctor["id"]}

