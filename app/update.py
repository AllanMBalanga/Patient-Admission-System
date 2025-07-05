from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from datetime import datetime

#Provinces
class ProvincesPut(BaseModel):
    name: str
    city: str

class ProvincesPatch(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None

#Patients
class PatientsPut(BaseModel):
    province_id: int
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    gender: Literal["Male", "Female", "Others"] = None
    birth_date: datetime
    allergies: str = None
    height_cm: float
    weight_kg: float

class PatientsPatch(BaseModel):
    province_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    gender: Optional[Literal["Male", "Female", "Others"]] = None
    birth_date: Optional[datetime] = None
    allergies: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None

#Doctors
class DoctorsPut(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    specialty: str

class DoctorsPatch(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    specialty: Optional[str] = None

#admission
class AdmissionPut(BaseModel):
    diagnosis: str
    status: Literal["sick", "healthy"] = "sick"
    admission_date: datetime
    discharge_date: Optional[datetime] = None

class AdmissionPatch(BaseModel):
    diagnosis: Optional[str] = None
    status: Optional[Literal["sick", "healthy"]] = "sick"
    admission_date: Optional[datetime] = None
    discharge_date: Optional[datetime] = None

#Patients of a doctor
class DoctorsPatientPut(BaseModel):
    allergies: str = None
    height_cm: float
    weight_kg: float

class DoctorsPatientPatch(BaseModel):
    allergies: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None

def dynamic_patch_query(table: str, data: dict, table_id: int, patient_id: int = None, doctor_id: int = None) -> tuple[str, tuple]:
    set_clause = ", ".join(f"{k} = %s" for k in data.keys())    # Sanitize column names (basic safeguard against SQL injection)

    sql = f"UPDATE {table} SET {set_clause}"        # Build base SQL

    if table == "admissions" and patient_id is not None and doctor_id is not None:          # Add WHERE clause based on table and optional IDs
        sql += " WHERE id = %s AND patient_id = %s AND doctor_id = %s"
        values = tuple(data.values()) + (table_id, patient_id, doctor_id)
    else:
        sql += " WHERE id = %s"
        values = tuple(data.values()) + (table_id,)

    return sql, values
