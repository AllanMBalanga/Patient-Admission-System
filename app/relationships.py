from .database import Database

def patient_relationship(patient, db: Database):
    db.cursor.execute("SELECT * FROM provinces WHERE id = %s", (patient["province_id"],))
    province = db.cursor.fetchone()

    db.cursor.execute("SELECT * FROM admissions WHERE patient_id = %s", (patient["id"],))
    admissions = db.cursor.fetchall()
    
    new_admissions = []
    for admission in admissions:
        db.cursor.execute("SELECT * FROM doctors WHERE id = %s", (admission["doctor_id"],))
        doctor = db.cursor.fetchone()

        new_admissions.append({
            **admission,
            "doctor": doctor
        })

    return {
        **patient,
        "province": province,
        "admissions": new_admissions
    } 


def doctor_relationship(doctor, db: Database):
    db.cursor.execute("SELECT * FROM admissions WHERE doctor_id = %s", (doctor["id"],))
    admissions = db.cursor.fetchall()

    new_admissions = []

    for admission in admissions:
        db.cursor.execute("SELECT * FROM patients WHERE id = %s", (admission["patient_id"],))
        patient = db.cursor.fetchone()

        new_admissions.append({
            **admission,
            "patient": patient
        })

    return {
        **doctor,
        "admissions": new_admissions
    }


def admission_relationship(admission, db: Database):
    db.cursor.execute("SELECT * FROM patients WHERE id = %s", (admission["patient_id"],))
    patient = db.cursor.fetchone()

    db.cursor.execute("SELECT * FROM doctors WHERE id = %s", (admission["doctor_id"],))
    doctor = db.cursor.fetchone()

    return {
        **admission,
        "patient": patient,
        "doctor": doctor
    } 
