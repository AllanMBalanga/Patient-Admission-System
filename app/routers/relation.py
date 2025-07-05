from fastapi import APIRouter, status, HTTPException, Depends
from ..response import AdmissionResponse, DoctorPatientDetailResponse
from ..relationships import admission_relationship, patient_relationship
from ..body import AdmittedPatient, TokenData
from typing import List
from ..database import Database
from ..oauth2 import get_current_doctor
from ..status_codes import validate_logged_in_user, validate_patient_exists, validate_doctor_admissions

#patients from a particular doctor
#SELECT * FROM patients JOIN admissions ON admission.patient_id = patients.id WHERE doctors.id = doctor_id

#doctor's patient(s) - only assigning a patient to a doctor and getting the information of patients (get all/by id)
router = APIRouter(
    prefix="/doctors/{doctor_id}/patients",
    tags=["Patients of Doctors"]
)

db = Database()

@router.get("/", response_model=List[DoctorPatientDetailResponse])
def patients_of_doctor(doctor_id: int, current_doctor: TokenData = Depends(get_current_doctor)):
    validate_logged_in_user(doctor_id, current_doctor.id)
    db.cursor.execute("""
            SELECT 
                patients.*,
                admissions.id AS admission_id
            FROM patients 
            JOIN admissions ON admissions.patient_id = patients.id 
            WHERE admissions.doctor_id = %s
            """, (doctor_id,)
    )
    patients = db.cursor.fetchall()
    
    relationship_response = []
    for patient in patients:
        new_patient = patient_relationship(patient, db)
        relationship_response.append(DoctorPatientDetailResponse(**new_patient))        #[RelationResponse(**row) for row in patients] - before relationship implementation

    return relationship_response

#Assign an existing patient to a doctor (admission)
@router.post("/", response_model=AdmissionResponse)
def assign_a_patient(doctor_id: int, assign_patient: AdmittedPatient, current_doctor: TokenData = Depends(get_current_doctor)):
    try:
        validate_logged_in_user(doctor_id, current_doctor.id)
        db.cursor.execute("SELECT * FROM patients WHERE id = %s", (assign_patient.patient_id,))
        existing_patient = db.cursor.fetchone()
        validate_patient_exists(existing_patient, assign_patient.patient_id)
        
        if assign_patient.admission_date:
            db.cursor.execute(
                "INSERT INTO admissions (patient_id, doctor_id, diagnosis, status, admission_date) VALUES (%s, %s, %s, %s, %s)",
                (
                    assign_patient.patient_id,
                    current_doctor.id,
                    assign_patient.diagnosis,
                    assign_patient.status,
                    assign_patient.admission_date
                )
            )
        else:
            db.cursor.execute(
                "INSERT INTO admissions (patient_id, doctor_id, diagnosis, status) VALUES (%s, %s, %s, %s)",
                (
                    assign_patient.patient_id,
                    current_doctor.id,
                    assign_patient.diagnosis,
                    assign_patient.status
                )
            )
        db.conn.commit()

        db.cursor.execute(
            "SELECT * FROM admissions WHERE patient_id = %s AND doctor_id = %s ORDER BY admission_date DESC LIMIT 1", 
            (assign_patient.patient_id, current_doctor.id))
        assigned_patient = db.cursor.fetchone()

        relationship_response = admission_relationship(assigned_patient, db)

        return AdmissionResponse(**relationship_response)
    
    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

@router.get("/{patient_id}", response_model=DoctorPatientDetailResponse)
def patient_of_doctor(doctor_id: int, patient_id: int, current_doctor: TokenData = Depends(get_current_doctor)):
    validate_logged_in_user(doctor_id, current_doctor.id)
    db.cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
    existing_patient = db.cursor.fetchone()
    validate_patient_exists(existing_patient, patient_id)

    db.cursor.execute("""
                SELECT 
                    patients.*,
                    admissions.id AS admission_id
                FROM patients 
                JOIN admissions 
                ON admissions.patient_id = patients.id 
                WHERE admissions.doctor_id = %s AND admissions.patient_id = %s 
                LIMIT 1""", 
        (current_doctor.id, patient_id)
    )
    patient = db.cursor.fetchone()
    validate_doctor_admissions(patient)

    relationship_response = patient_relationship(patient, db)

    return DoctorPatientDetailResponse(**relationship_response)

#DONT ALLOW DOCTORS TO WRITE OPERATIONS ON PATIENTS (other doctors may rely on the patient's info)

# @router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_assigned_patient(doctor_id: int, patient_id: int, current_doctor: TokenData = Depends(get_current_doctor)):
#     try:
#         #CHECK if doctor_id is the same as the logged in doctor_id
#         if doctor_id != current_doctor.id:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")

#         db.cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
#         existing_patient = db.cursor.fetchone()
#         if not existing_patient:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient was not found")

#         #CHECK if doctor_id logged in handles the patient_id to be deleted
#         db.cursor.execute("SELECT * FROM admissions WHERE doctor_id = %s AND patient_id = %s", (current_doctor.id, patient_id))
#         authorized_rows = db.cursor.fetchall()
#         if not authorized_rows:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor not authorized to delete this patient")
        
#         db.cursor.execute("DELETE FROM patients WHERE id = %s", (patient_id,))
#         db.conn.commit()  

#         return
    
#     except HTTPException as http_error:
#         raise http_error
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"{e}")

# @router.put("/{patient_id}", response_model=PatientResponse)
# def put_assigned_patient(doctor_id: int, patient_id: int, assigned_patient: DoctorsPatientPut, current_doctor: TokenData = Depends(get_current_doctor)):
#     try:
#         #CHECK if doctor_id is the same as the logged in doctor_id
#         if doctor_id != current_doctor.id:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")
        
#         db.cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
#         existing_patient = db.cursor.fetchone()
#         if not existing_patient:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient was not found")
        
#         #CHECK if doctor_id logged in handles the patient_id to be updated
#         db.cursor.execute("SELECT * FROM admissions WHERE doctor_id = %s AND patient_id = %s", (current_doctor.id, patient_id))
#         authorized_rows = db.cursor.fetchall()
#         if not authorized_rows:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor not authorized to update this patient")
        
#         db.cursor.execute(
#             "UPDATE patients SET allergies = %s, height_cm = %s, weight_kg = %s WHERE id = %s",
#             (assigned_patient.allergies, assigned_patient.height_cm, assigned_patient.weight_kg, patient_id))
#         db.conn.commit()
        
#         db.cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
#         updated_patient = db.cursor.fetchone()
        
#         return PatientResponse(**updated_patient)

#     except HTTPException as http_error:
#         raise http_error
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"{e}")

# @router.patch("/{patient_id}", response_model=PatientResponse)
# def patch_assigned_patient(doctor_id: int, patient_id: int, assigned_patient: DoctorsPatientPatch, current_doctor: TokenData = Depends(get_current_doctor)):
#     try:
#         #CHECK if doctor_id is the same as the logged in doctor_id
#         if doctor_id != current_doctor.id:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")
        
#         db.cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
#         existing_patient = db.cursor.fetchone()
#         if not existing_patient:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient was not found")
        
#         #CHECK if doctor_id logged in handles the patient_id to be updated
#         db.cursor.execute("SELECT * FROM admissions WHERE doctor_id = %s AND patient_id = %s", (current_doctor.id, patient_id))
#         authorized_rows = db.cursor.fetchall()
#         if not authorized_rows:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor not authorized to update this patient")
        
#         excluded_values= assigned_patient.dict(exclude_unset=True)

#         set_clause = ", ".join(f"{k} = %s" for k in excluded_values) 
#         sql = f"UPDATE patients SET {set_clause} WHERE id = %s"
#         values = tuple(excluded_values.values()) + (patient_id,)

#         db.cursor.execute(sql, values)
#         db.conn.commit()

#         db.cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
#         updated_patient = db.cursor.fetchone()

#         return PatientResponse(**updated_patient)

#     except HTTPException as http_exception:
#         raise http_exception
    
#     except Exception:
#         db.conn.rollback()
#         raise HTTPException(status_code=500, detail="Internal server error")