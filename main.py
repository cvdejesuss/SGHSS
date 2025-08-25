from fastapi import FastAPI
from routers import patient_router, auth_router, appointment_router, record_router

app = FastAPI()

app.include_router(patient_router.router)
app.include_router(auth_router.router)
app.include_router(appointment_router.router)
app.include_router(record_router.router)


@app.get("/")
def read_root():
    return {"msg": "SGHSS Backend está rodando"}
