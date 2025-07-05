from fastapi import status, HTTPException

#check if province exists
def validate_province_exists(province, province_id: int = None):
    if not province:
        if province_id:
            detail = f"Province with id {province_id} was not found"
        else:
            detail = "Province was not found"
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )
    
def validate_patient_exists(patient, patient_id: int = None):
    if not patient:
        if patient_id:
            detail = f"Patient with id {patient_id} was not found"
        else:
            detail = "Patient was not found"
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

def validate_logged_in_user(user_id: int, current_user: int):
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action"
        )
    
def validate_excluded_values(excluded_values):
    if not excluded_values:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No data was found for the update"
        )
    
def validate_doctor_exists(doctor, doctor_id: int = None):
    if not doctor:
        if doctor_id:
            detail = f"Doctor with id {doctor_id} was not found"
        else:
            detail = "Doctor was not found"
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

#if there are no patients that have the doctor_id logged in (the doctor does not handle that person)
def validate_doctor_admissions(admission):
    if not admission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor is not assigned to this patient"
        )

def validate_patient_admissions(admission):
    if not admission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admission of patient was not found"
        )