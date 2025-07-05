from fastapi import FastAPI
from .database import Database
from .routers import d_admissions, provinces, patients, doctors, relation, login, p_admissions

app = FastAPI()

app.include_router(provinces.router)
app.include_router(patients.router)
app.include_router(p_admissions.router)
app.include_router(doctors.router)
app.include_router(relation.router)
app.include_router(d_admissions.router)
app.include_router(login.router)

@app.on_event("startup")
def startup():
    db = Database()
    db.create_tables()
