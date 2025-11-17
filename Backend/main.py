from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Backend.routes import admin, positions, attendance, student, teacher

app = FastAPI()

# Allow frontend (localhost:3000) to call backend (127.0.0.1:8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all route modules
app.include_router(admin.router)
app.include_router(positions.router)
app.include_router(attendance.router)
app.include_router(student.router)
app.include_router(teacher.router)

@app.get("/")
def root():
    return {"message": "Student tracker api running"}