# Backend/scripts/reset_attendance_table.py

from sqlalchemy import text
from Backend.db import engine, Base
from Backend import models  # make sure models are imported so Attendance is registered


def main() -> None:
    # Drop the old Attendance table if it exists
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS Attendance"))

    # Recreate missing tables from the SQLAlchemy models (including Attendance)
    Base.metadata.create_all(bind=engine)

    print("✅ Attendance table has been reset to match the SQLAlchemy models.")


if __name__ == "__main__":
    main()
