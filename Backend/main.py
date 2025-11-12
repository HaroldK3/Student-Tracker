from fastapi import FastAPI
from Backend.routes import admin, positions, attendance, student, teacher

app = FastAPI()

app.include_router(admin.router)
app.include_router(positions.router)
##app.include_router(.router)

@app.get("/")
def root():
    return {"message": "Student tracker api running"}
