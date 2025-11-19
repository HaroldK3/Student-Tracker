"""Backfill historical location data into StudentLocations.

Usage: run from repository root with the virtualenv active:
  .\.venv\Scripts\Activate.ps1
  python Backend\scripts\backfill_locations.py [--dry-run] [--csv output.csv] [--dedupe-window seconds]

Options:
  --dry-run           : Do not insert rows; write candidate rows to CSV instead.
  --csv <file>        : CSV file path to write candidates when --dry-run is used (default: backfill_candidates.csv).
  --dedupe-window S   : Consider existing rows within S seconds as duplicates (default 0 = exact timestamp match).

This script is defensive: it will skip strategies that are not present in the database schema.
"""
import argparse
import csv
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from Backend.db import engine, SessionLocal
from Backend import models
from datetime import datetime, timedelta


def table_columns(conn, table_name: str):
    res = conn.execute(text(f"PRAGMA table_info('{table_name}')")).fetchall()
    return [r[1] for r in res]


def find_tables_with_latlng(conn):
    tables = [r[0] for r in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()]
    matches = []
    for t in tables:
        try:
            cols = table_columns(conn, t)
            if 'Lat' in cols and 'Lng' in cols:
                matches.append((t, cols))
        except Exception:
            continue
    return matches


def is_duplicate(session, sid, when, window_seconds: int):
    if window_seconds and window_seconds > 0:
        start = when - timedelta(seconds=window_seconds)
        end = when + timedelta(seconds=window_seconds)
        exists = session.query(models.StudentLocation).filter(
            models.StudentLocation.StudentId == sid,
            models.StudentLocation.CheckInUtc >= start,
            models.StudentLocation.CheckInUtc <= end,
        ).first()
    else:
        exists = session.query(models.StudentLocation).filter(
            models.StudentLocation.StudentId == sid,
            models.StudentLocation.CheckInUtc == when,
        ).first()
    return exists is not None


def collect_candidates_from_attendance(conn):
    cols = table_columns(conn, 'Attendance')
    candidates = []
    if 'Lat' not in cols or 'Lng' not in cols:
        return candidates

    if 'StudentId' in cols:
        rows = conn.execute(text("SELECT AttendanceId, StudentId, Lat, Lng, CreatedAtUtc FROM Attendance WHERE Lat IS NOT NULL AND Lng IS NOT NULL")).fetchall()
        for r in rows:
            m = r._mapping
            candidates.append({
                'source_table': 'Attendance',
                'source_id': m.get('AttendanceId'),
                'StudentId': m.get('StudentId'),
                'Lat': m.get('Lat'),
                'Lng': m.get('Lng'),
                'CheckInUtc': m.get('CreatedAtUtc') or datetime.utcnow(),
            })
        return candidates

    if 'AssignmentId' in cols:
        rows = conn.execute(text(
            "SELECT a.AttendanceId, a.AssignmentId, a.Lat, a.Lng, a.CreatedAtUtc, sa.StudentId "
            "FROM Attendance a JOIN StudentAssignments sa ON a.AssignmentId = sa.AssignmentId "
            "WHERE a.Lat IS NOT NULL AND a.Lng IS NOT NULL"
        )).fetchall()
        for r in rows:
            m = r._mapping
            candidates.append({
                'source_table': 'Attendance',
                'source_id': m.get('AttendanceId'),
                'StudentId': m.get('StudentId'),
                'Lat': m.get('Lat'),
                'Lng': m.get('Lng'),
                'CheckInUtc': m.get('CreatedAtUtc') or datetime.utcnow(),
            })
    return candidates


def collect_candidates_from_other_tables(conn):
    matches = find_tables_with_latlng(conn)
    candidates = []
    for t, cols in matches:
        if t in ('Attendance', 'StudentLocations'):
            continue
        if 'StudentId' in cols:
            rows = conn.execute(text(f"SELECT * FROM {t} WHERE Lat IS NOT NULL AND Lng IS NOT NULL")).fetchall()
            for r in rows:
                m = r._mapping
                candidates.append({
                    'source_table': t,
                    'source_id': m.get(next(iter(m.keys()), None)),
                    'StudentId': m.get('StudentId'),
                    'Lat': m.get('Lat'),
                    'Lng': m.get('Lng'),
                    'CheckInUtc': m.get('CreatedAtUtc') or m.get('CheckInUtc') or datetime.utcnow(),
                })
        elif 'AssignmentId' in cols:
            rows = conn.execute(text(
                f"SELECT t.*, sa.StudentId FROM {t} t JOIN StudentAssignments sa ON t.AssignmentId = sa.AssignmentId WHERE t.Lat IS NOT NULL AND t.Lng IS NOT NULL"
            )).fetchall()
            for r in rows:
                m = r._mapping
                candidates.append({
                    'source_table': t,
                    'source_id': m.get(next(iter(m.keys()), None)),
                    'StudentId': m.get('StudentId'),
                    'Lat': m.get('Lat'),
                    'Lng': m.get('Lng'),
                    'CheckInUtc': m.get('CreatedAtUtc') or m.get('CheckInUtc') or datetime.utcnow(),
                })
    return candidates


def write_csv(candidates, csv_path):
    if not candidates:
        print("No candidate rows to write to CSV")
        return
    keys = ['source_table', 'source_id', 'StudentId', 'Lat', 'Lng', 'CheckInUtc']
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for c in candidates:
            row = {k: c.get(k) for k in keys}
            # format datetime
            if isinstance(row.get('CheckInUtc'), datetime):
                row['CheckInUtc'] = row['CheckInUtc'].isoformat()
            writer.writerow(row)
    print(f"Wrote {len(candidates)} candidate rows to {csv_path}")


def perform_insert(candidates, session, dedupe_window):
    inserted = 0
    for c in candidates:
        sid = c.get('StudentId')
        if sid is None:
            continue
        when = c.get('CheckInUtc') or datetime.utcnow()
        if isinstance(when, str):
            try:
                when = datetime.fromisoformat(when)
            except Exception:
                when = datetime.utcnow()

        if is_duplicate(session, sid, when, dedupe_window):
            continue

        loc = models.StudentLocation(
            StudentId=sid,
            Lat=c.get('Lat') or 0.0,
            Lng=c.get('Lng') or 0.0,
            CheckInUtc=when,
            CreatedAtUtc=datetime.utcnow(),
        )
        session.add(loc)
        inserted += 1
    session.commit()
    return inserted


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Do not insert rows; write candidates to CSV')
    parser.add_argument('--csv', default='Backend/scripts/backfill_candidates.csv', help='CSV output path for dry-run')
    parser.add_argument('--dedupe-window', type=int, default=0, help='Seconds window to dedupe inserts')
    args = parser.parse_args()

    print("Backfill: starting")
    conn = engine.connect()
    session = SessionLocal()
    total_candidates = []
    total_inserted = 0
    try:
        models.Base.metadata.create_all(bind=engine)

        c1 = collect_candidates_from_attendance(conn)
        print(f"Found {len(c1)} candidates in Attendance")
        total_candidates.extend(c1)

        c2 = collect_candidates_from_other_tables(conn)
        print(f"Found {len(c2)} candidates in other tables")
        total_candidates.extend(c2)

        if args.dry_run:
            write_csv(total_candidates, args.csv)
            print(f"Dry-run complete: {len(total_candidates)} candidates written. No inserts performed.")
            return

        if total_candidates:
            inserted = perform_insert(total_candidates, session, args.dedupe_window)
            total_inserted += inserted
            print(f"Inserted {inserted} rows into StudentLocations")

        print(f"Backfill: finished, total inserted = {total_inserted}")
    except SQLAlchemyError as e:
        print("Backfill failed:", e)
    finally:
        session.close()
        conn.close()


if __name__ == '__main__':
    main()
