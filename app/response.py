
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Literal, List


class BaseProvinceResponse(BaseModel):
    id: int
    name: str
    city: str

class BasePatientResponse(BaseModel):
    id: int
    province_id: int
    first_name: str
    last_name: str
    email: EmailStr
    gender: Optional[Literal["Male", "Female", "Others"]] = None
    birth_date: datetime
    allergies: str
    height_cm: float
    weight_kg: float

class BaseDoctorResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    specialty: str

class BasePatientAdmissionResponse(BaseModel):
    id: int
    doctor_id: int
    diagnosis: str
    status: Literal["sick", "healthy"]
    admission_date: datetime
    discharge_date: Optional[datetime] = None

    doctor: BaseDoctorResponse

class BaseDoctorAdmissionResponse(BaseModel):
    id: int
    patient_id: int
    diagnosis: str
    status: Literal["sick", "healthy"]
    admission_date: datetime
    discharge_date: Optional[datetime] = None

    patient: BasePatientResponse

    
#Response model relationships
class ProvinceResponse(BaseModel):
    id: int
    name: str
    city: str

class PatientResponse(BaseModel):
    id: int
    province_id: int
    first_name: str
    last_name: str
    email: EmailStr
    gender: Optional[Literal["Male", "Female", "Others"]] = None
    birth_date: datetime
    allergies: str
    height_cm: float
    weight_kg: float

    province: BaseProvinceResponse      #only one - not list
    admissions: Optional[List[BasePatientAdmissionResponse]] = Field(default_factory=list)     #doctors and admissions - can be multiple - list

class DoctorResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    specialty: str

    admissions: Optional[List[BaseDoctorAdmissionResponse]] = Field(default_factory=list)

class AdmissionResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    diagnosis: str
    status: Literal["sick", "healthy"]
    admission_date: datetime
    discharge_date: Optional[datetime] = None

    patient: BasePatientResponse
    doctor: BaseDoctorResponse

class DoctorPatientDetailResponse(PatientResponse):
    admission_id: int

