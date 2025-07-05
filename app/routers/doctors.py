from fastapi import APIRouter, status, HTTPException, Depends
from ..body import Doctor, TokenData
from ..response import DoctorResponse
from ..update import DoctorsPatch, DoctorsPut, dynamic_patch_query
from typing import List
from ..database import Database
from ..utils import hash
from ..oauth2 import get_current_doctor
from ..relationships import doctor_relationship
from ..status_codes import validate_excluded_values, validate_doctor_exists, validate_logged_in_user

#doctors requests (get all/by id, post, delete, put, patch)
router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
)

db = Database()

@router.get("/", response_model=List[DoctorResponse])
def get_doctors():
    db.cursor.execute("SELECT * FROM doctors")
    doctors = db.cursor.fetchall()

    relationship_response = []

    for doctor in doctors:
        new_doctor = doctor_relationship(doctor, db)
        relationship_response.append(DoctorResponse(**new_doctor))

    return relationship_response

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=DoctorResponse)
def create_doctor(doctor: Doctor):
    try:
        doctor.password = hash(doctor.password)
        db.cursor.execute(
            "INSERT INTO doctors (first_name, last_name, email, password, specialty) VALUES (%s, %s, %s, %s, %s)", 
            (doctor.first_name, doctor.last_name, doctor.email, doctor.password, doctor.specialty)
        )
        db.conn.commit()

        db.cursor.execute("SELECT * FROM doctors WHERE id = LAST_INSERT_ID()")
        created_doctor = db.cursor.fetchone()
        
        return DoctorResponse(**created_doctor)
    
    except HTTPException as http_error:
        raise http_error
    
    except Exception:
        db.conn.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error")

@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor_by_id(doctor_id: int):
    db.cursor.execute("SELECT * FROM doctors WHERE id = %s", (doctor_id,))
    doctor = db.cursor.fetchone()
    validate_doctor_exists(doctor, doctor_id)

    relationship_response = doctor_relationship(doctor, db)

    return DoctorResponse(**relationship_response)

@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor(doctor_id: int, current_user: TokenData = Depends(get_current_doctor)):
    try:
        validate_logged_in_user(doctor_id, current_user.id)
        db.cursor.execute("SELECT * FROM doctors WHERE id = %s", (doctor_id,))
        doctor = db.cursor.fetchone()
        validate_doctor_exists(doctor, doctor_id)
        
        db.cursor.execute("DELETE FROM doctors WHERE id = %s", (doctor_id,))
        db.conn.commit()
    
        return

    except HTTPException as http_error:
        raise http_error
    
    except Exception:
        db.conn.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.put("/{doctor_id}", response_model=DoctorResponse)
def put_patient(doctor_id: int, doctor: DoctorsPut, current_user: TokenData = Depends(get_current_doctor)):
    try:
        validate_logged_in_user(doctor_id, current_user.id)
        db.cursor.execute("SELECT * FROM doctors WHERE id = %s", (doctor_id,))
        existing_doctor = db.cursor.fetchone()
        validate_doctor_exists(existing_doctor, doctor_id)
        
        doctor.password = hash(doctor.password)
        db.cursor.execute(
            "UPDATE doctors SET first_name = %s, last_name = %s, email = %s, password = %s, specialty = %s WHERE id = %s", 
            (doctor.first_name, doctor.last_name, doctor.email, doctor.password, doctor.specialty, doctor_id)
        )
        db.conn.commit()
        db.cursor.execute("SELECT * FROM doctors WHERE id = %s", (doctor_id,))
        updated_doctor = db.cursor.fetchone()

        relationship_response = doctor_relationship(updated_doctor, db)

        return DoctorResponse(**relationship_response)
    
    except HTTPException as http_error:
        raise http_error
    
    except Exception:
        db.conn.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
    

@router.patch("/{doctor_id}", response_model=DoctorResponse)
def patch_patient(doctor_id: int, doctor: DoctorsPatch, current_user: TokenData = Depends(get_current_doctor)):
    try:
        validate_logged_in_user(doctor_id, current_user.id)
        db.cursor.execute("SELECT * FROM doctors WHERE id = %s", (doctor_id,))
        existing_doctor = db.cursor.fetchone()
        validate_doctor_exists(existing_doctor, doctor_id)

        if doctor.password:
            doctor.password = hash(doctor.password)

        excluded_values = doctor.dict(exclude_unset=True)
        validate_excluded_values(excluded_values)
        
        sql, values = dynamic_patch_query("doctors", excluded_values, current_user.id)
        db.cursor.execute(sql, values)
        db.conn.commit()

        db.cursor.execute("SELECT * FROM doctors WHERE id = %s", (doctor_id,))
        updated_doctor = db.cursor.fetchone()

        relationship_response = doctor_relationship(updated_doctor, db)

        return DoctorResponse(**relationship_response)
    
    except HTTPException as http_exception:
        raise http_exception
    
    except Exception:
        db.conn.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
