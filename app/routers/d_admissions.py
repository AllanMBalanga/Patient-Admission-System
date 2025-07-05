from fastapi import APIRouter, status, HTTPException, Depends
from ..body import DoctorAdmission, TokenData
from ..update import AdmissionPut, AdmissionPatch, dynamic_patch_query
from ..response import AdmissionResponse
from ..database import Database
from typing import List
from datetime import datetime
from ..oauth2 import get_current_doctor
from ..relationships import admission_relationship
from ..status_codes import validate_excluded_values, validate_logged_in_user, validate_doctor_admissions, validate_patient_exists

#manages the admissions of patients (get all/by id, post, delete, put, patch)
router = APIRouter(
    prefix="/doctors/{doctor_id}/patients/{patient_id}/admissions",
    tags=["Doctor Admission Requests"]
)

db = Database()

@router.get("/", response_model=List[AdmissionResponse])
def get_admissions(doctor_id: int, patient_id: int, current_doctor: TokenData = Depends(get_current_doctor)):
    validate_logged_in_user(doctor_id, current_doctor.id)
    db.cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
    patient = db.cursor.fetchone()
    validate_patient_exists(patient, patient_id)

    #if there are no patients that have the doctor_id logged in (the doctor does not handle that person)
    db.cursor.execute("SELECT * FROM admissions WHERE patient_id = %s AND doctor_id = %s", (patient_id, current_doctor.id))
    admissions = db.cursor.fetchall()
    validate_doctor_admissions(admissions)

    relationship_response = []
    for admission in admissions:
        new_admission = admission_relationship(admission, db)
        relationship_response.append(AdmissionResponse(**new_admission))        #[AdmissionResponse(**row) for row in admissions] - before relationship implementation

    return relationship_response

@router.post("/", response_model=AdmissionResponse, status_code=status.HTTP_201_CREATED)
def create_admissions(doctor_id: int, patient_id: int, admission: DoctorAdmission, current_doctor: TokenData = Depends(get_current_doctor)):
    try:
        validate_logged_in_user(doctor_id, current_doctor.id)
        db.cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
        patient = db.cursor.fetchone()
        validate_patient_exists(patient, patient_id)

        db.cursor.execute(
            "INSERT INTO admissions (patient_id, doctor_id, diagnosis, status) VALUES (%s, %s, %s, %s)",
            (patient_id, doctor_id, admission.diagnosis, admission.status))
        db.conn.commit()

        db.cursor.execute("SELECT * FROM admissions WHERE patient_id = %s AND doctor_id = %s ORDER BY admission_date DESC LIMIT 1", (patient_id, current_doctor.id))
        admission = db.cursor.fetchone()

        relationship_response = admission_relationship(admission, db)

        return AdmissionResponse(**relationship_response)
    
    except HTTPException as http_exception:
        raise http_exception
    
    except Exception as e:
        db.conn.rollback()
        raise HTTPException(status_code=500, detail=f"{e}")

@router.get("/{admission_id}", response_model=AdmissionResponse)
def get_admission_by_id(doctor_id: int, patient_id: int, admission_id: int, current_doctor: TokenData = Depends(get_current_doctor)):
    validate_logged_in_user(doctor_id, current_doctor.id)
    db.cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
    patient = db.cursor.fetchone()
    validate_patient_exists(patient, patient_id)

    db.cursor.execute("SELECT * FROM admissions WHERE id = %s AND patient_id = %s AND doctor_id = %s", (admission_id, patient_id, current_doctor.id))
    admission = db.cursor.fetchone()
    validate_doctor_admissions(admission)

    relationship_response = admission_relationship(admission, db)

    return AdmissionResponse(**relationship_response)

@router.delete("/{admission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admission(doctor_id: int, patient_id: int, admission_id: int, current_doctor: TokenData = Depends(get_current_doctor)):
    try:
        validate_logged_in_user(doctor_id, current_doctor.id)
        db.cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
        patient = db.cursor.fetchone()
        validate_patient_exists(patient, patient_id)

        db.cursor.execute("SELECT * FROM admissions WHERE id = %s AND patient_id = %s AND doctor_id = %s", (admission_id, patient_id, current_doctor.id))
        admission = db.cursor.fetchone()
        validate_doctor_admissions(admission)

        db.cursor.execute("DELETE FROM admissions WHERE id = %s AND patient_id = %s AND doctor_id = %s", (admission_id, patient_id, current_doctor.id))
        db.conn.commit()

        return

    except HTTPException as http_exception:
        raise http_exception
    
    except Exception:
        db.conn.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
    

@router.put("/{admission_id}", response_model=AdmissionResponse)
def put_admission(doctor_id: int, patient_id: int, admission_id: int, admission: AdmissionPut, current_doctor: TokenData = Depends(get_current_doctor)):
    try:
        validate_logged_in_user(doctor_id, current_doctor.id)
        db.cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
        patient = db.cursor.fetchone()
        validate_patient_exists(patient, patient_id)

        db.cursor.execute("SELECT * FROM admissions WHERE id = %s AND patient_id = %s AND doctor_id = %s", (admission_id, patient_id, current_doctor.id))
        existing_admission = db.cursor.fetchone()
        validate_doctor_admissions(existing_admission)
        
        if admission.status:
            if existing_admission["status"] == "healthy" and admission.status == "sick":
                admission.discharge_date = None
            elif existing_admission["status"] == "sick" and admission.status == "healthy":
                admission.discharge_date = datetime.utcnow()

        db.cursor.execute(
            "UPDATE admissions SET diagnosis = %s, status = %s, admission_date = %s, discharge_date = %s WHERE id = %s AND patient_id = %s AND doctor_id = %s",
            (admission.diagnosis, admission.status, admission.admission_date, admission.discharge_date, admission_id, patient_id, current_doctor.id))
        db.conn.commit()
        
        db.cursor.execute("SELECT * FROM admissions WHERE id = %s AND patient_id = %s AND doctor_id = %s", (admission_id, patient_id, current_doctor.id))
        updated_admission = db.cursor.fetchone()

        relationship_response = admission_relationship(updated_admission, db)

        return AdmissionResponse(**relationship_response)

    except HTTPException as http_exception:
        raise http_exception
    
    except Exception as e:
        db.conn.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{admission_id}", response_model=AdmissionResponse)
def patch_admission(doctor_id: int, patient_id: int, admission_id: int, admission: AdmissionPatch, current_doctor: TokenData = Depends(get_current_doctor)):
    try:
        validate_logged_in_user(doctor_id, current_doctor.id)
        db.cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
        patient = db.cursor.fetchone()
        validate_patient_exists(patient, patient_id)

        db.cursor.execute("SELECT * FROM admissions WHERE id = %s AND patient_id = %s AND doctor_id = %s", (admission_id, patient_id, current_doctor.id))
        existing_admission = db.cursor.fetchone()
        validate_doctor_admissions(existing_admission)

        excluded_values = admission.dict(exclude_unset=True)
        validate_excluded_values(excluded_values)
        
        if "status" in excluded_values:
            new_status = excluded_values["status"]
            if existing_admission["status"] == "healthy" and new_status == "sick":
                excluded_values["discharge_date"] = None
            elif existing_admission["status"] == "sick" and new_status == "healthy":
                excluded_values["discharge_date"] = datetime.utcnow()

        sql, values = dynamic_patch_query("admissions", excluded_values, admission_id, patient_id=patient_id, doctor_id=current_doctor.id)
        db.cursor.execute(sql, values)
        db.conn.commit()

        db.cursor.execute("SELECT * FROM admissions WHERE id = %s AND patient_id = %s AND doctor_id = %s", (admission_id, patient_id, current_doctor.id))
        updated_admission = db.cursor.fetchone()

        relationship_response = admission_relationship(updated_admission, db)

        return AdmissionResponse(**relationship_response)

    except HTTPException as http_error:
        raise http_error

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")