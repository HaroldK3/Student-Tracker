from fastapi import FastAPI
from Backend.routes import admin

app = FastAPI()

app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": "Student tracker api running"}
