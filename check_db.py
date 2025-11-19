import sqlite3, os, json
db="C:\\Users\\pcnew\\OneDrive\\Desktop\\ETSU\\4250-001\\Student-Tracker\\Backend\\student_tracker.db"
print("DB path:", db)
if not os.path.exists(db):
    print("DB not found")
else:
    conn=sqlite3.connect(db)
    cur=conn.cursor()
    try:
        tables=[r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        print("Tables:", tables)
        if "Users" in tables:
            rows=cur.execute("SELECT UserId, FirstName, LastName, Email, Role, IsActive, CreatedAtUtc FROM Users LIMIT 20").fetchall()
            print("Users:")
            for r in rows:
                print(json.dumps({
                    "UserId": r[0],
                    "FirstName": r[1],
                    "LastName": r[2],
                    "Email": r[3],
                    "Role": r[4],
                    "IsActive": r[5],
                    "CreatedAtUtc": str(r[6])
                }, ensure_ascii=False))
        else:
            print("No Users table found")
    except Exception as e:
        print("ERROR querying DB:", e)
    finally:
        conn.close()
