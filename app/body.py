from pydantic import BaseModel, EmailStr
from typing import Literal, Optional
from datetime import datetime


class Province(BaseModel):
    name: str
    city: str

class Patient(BaseModel):
    province_id: int
    first_name: str
    last_name: str 
    email: EmailStr
    password: str
    gender: Optional[Literal["Male", "Female", "Others"]] = None
    birth_date: datetime
    allergies: Optional[str] = None
    height_cm: float
    weight_kg: float

class Doctor(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    specialty: str

class PatientAdmission(BaseModel):
    doctor_id: int
    diagnosis: str
    status: Literal["sick", "healthy"] = "sick"

class DoctorAdmission(BaseModel):
    diagnosis: str
    status: Literal["sick", "healthy"] = "sick"

class AdmittedPatient(BaseModel):
    patient_id: int
    diagnosis: str
    status: Literal["sick", "healthy"] = "sick"
    admission_date: Optional[datetime] = None

#Token
class PatientToken(BaseModel):
    access_token: str
    token_type: str
    patient_id: int

class DoctorToken(BaseModel):
    access_token: str
    token_type: str
    doctor_id: int

class TokenData(BaseModel):
    id: Optional[int] = None