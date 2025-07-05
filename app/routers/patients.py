from fastapi import APIRouter, status, HTTPException, Depends
from ..response import PatientResponse
from ..relationships import patient_relationship
from ..body import Patient, TokenData
from ..database import Database
from typing import List
from ..update import PatientsPut, PatientsPatch, dynamic_patch_query
from ..utils import hash
from ..oauth2 import get_current_patient
from ..status_codes import validate_excluded_values, validate_logged_in_user, validate_patient_exists, validate_province_exists

#patient requests (get all/by id, post, delete, put, patch)
router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)

db = Database()

@router.get("/", response_model=List[PatientResponse])
def get_patients():
    db.cursor.execute("SELECT * FROM patients")
    patients = db.cursor.fetchall()

    relationship_response = []
    for patient in patients:
        new_patient = patient_relationship(patient, db)
        relationship_response.append(PatientResponse(**new_patient))                #[PatientResponse(**row) for row in patients] original before relationship

    return relationship_response

@router.post("/", response_model=PatientResponse)
def create_patient(patient: Patient):
    try:
        db.cursor.execute("SELECT * FROM provinces WHERE id = %s", (patient.province_id,))
        province = db.cursor.fetchone()
        validate_province_exists(province, patient.province_id)

        patient.password = hash(patient.password)
        db.cursor.execute("""INSERT INTO patients (province_id, first_name, last_name, email, password, gender, birth_date, allergies, height_cm, weight_kg) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s,  %s, %s)""", (
                patient.province_id, 
                patient.first_name, 
                patient.last_name,
                patient.email,
                patient.password, 
                patient.gender, 
                patient.birth_date,
                patient.allergies, 
                patient.height_cm, 
                patient.weight_kg
            )
        )
        db.conn.commit()

        db.cursor.execute("SELECT * FROM patients WHERE id = LAST_INSERT_ID()")
        created_patient = db.cursor.fetchone()

        relationship_response = patient_relationship(created_patient, db)

        return PatientResponse(**relationship_response)

    except HTTPException as http_exception:
        raise http_exception
    
    except Exception as e:
        db.conn.rollback()
        raise HTTPException(status_code=500, detail=f"{e}")
    
@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient_by_id(patient_id: int):
    db.cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
    patient = db.cursor.fetchone()
    validate_patient_exists(patient, patient_id)

    relationship_response = patient_relationship(patient, db)

    return PatientResponse(**relationship_response)

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int, current_user: TokenData = Depends(get_current_patient)):
    try:   
        validate_logged_in_user(patient_id, current_user.id)
        db.cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
        patient = db.cursor.fetchone()
        validate_patient_exists(patient, patient_id)

        db.cursor.execute("DELETE FROM patients WHERE id = %s", (patient_id,))
        db.conn.commit()

        return
    
    except HTTPException as http_exception:
        raise http_exception
    
    except Exception:
        db.conn.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.put("/{patient_id}", response_model=PatientResponse)
def put_patient(patient_id: int, patient: PatientsPut, current_user: TokenData = Depends(get_current_patient)):
    try:
        validate_logged_in_user(patient_id, current_user.id)
        db.cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
        existing_patient = db.cursor.fetchone()
        validate_patient_exists(existing_patient, patient_id)

        db.cursor.execute("SELECT * FROM provinces WHERE id = %s", (patient.province_id,))
        province = db.cursor.fetchone()
        validate_province_exists(province, patient.province_id)

        patient.password = hash(patient.password)
        db.cursor.execute(
            "UPDATE patients SET province_id = %s, first_name = %s, last_name = %s, email = %s, password = %s, gender = %s, birth_date = %s, allergies = %s, height_cm = %s, weight_kg = %s WHERE id = %s", (
                patient.province_id, 
                patient.first_name, 
                patient.last_name, 
                patient.email, 
                patient.password, 
                patient.gender, 
                patient.birth_date,
                patient.allergies, 
                patient.height_cm, 
                patient.weight_kg, 
                patient_id
            )
        )
        db.conn.commit()
        db.cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
        updated_patient = db.cursor.fetchone()

        relationship_response = patient_relationship(updated_patient, db)

        return PatientResponse(**relationship_response)

    except HTTPException as http_exception:
        raise http_exception
    
    except Exception as e:
        db.conn.rollback()
        raise HTTPException(status_code=500, detail=f"{e}")
    
@router.patch("/{patient_id}", response_model=PatientResponse)
def patch_patient(patient_id: int, patient: PatientsPatch, current_user: TokenData = Depends(get_current_patient)):
    try:
        validate_logged_in_user(patient_id, current_user.id)
        db.cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
        existing_patient = db.cursor.fetchone()
        validate_patient_exists(existing_patient, patient_id)

        if patient.province_id:
            db.cursor.execute("SELECT * FROM provinces WHERE id = %s", (patient.province_id,))
            province = db.cursor.fetchone()
            validate_province_exists(province, patient.province_id)

        if patient.password:
            patient.password = hash(patient.password)

        excluded_values= patient.dict(exclude_unset=True)
        validate_excluded_values(excluded_values)
        
        sql, values = dynamic_patch_query("patients", excluded_values, current_user.id)
        db.cursor.execute(sql, values)
        db.conn.commit()

        db.cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
        updated_patient = db.cursor.fetchone()

        relationship_response = patient_relationship(updated_patient, db)
        return PatientResponse(**relationship_response)

    except HTTPException as http_exception:
        raise http_exception
    
    except Exception as e:
        db.conn.rollback()
        raise HTTPException(status_code=500, detail=f"{e}")
    
