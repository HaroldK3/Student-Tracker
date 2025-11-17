import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
});

// ------- Types that match your backend models -------

export interface User {
  UserId: number;
  FirstName: string;
  LastName: string;
  Email: string;
  Role: string;
  IsActive: boolean;
  CreatedAtUtc: string;
}

export interface Student {
  StudentId?: number;              // not in StudentOut but in DB
  UniversityId: number;
  FirstName: string;
  LastName: string;
  Email: string;
  PhoneE164?: string | null;
  Program: string;
  Year: string;
  Status: string;
  GPA?: number | null;
}

export interface AttendanceRecord {
  AttendanceId: number;
  StudentId: number;
  CheckInUtc: string;
  CheckOutUtc: string | null;
  IsApproved: boolean;
}

// ------- API calls -------

// ADMIN
export async function fetchUsers(): Promise<User[]> {
  const res = await api.get<User[]>("/admin/users");
  return res.data;
}

export async function createUser(data: Partial<User>) {
  const res = await api.post<User>("/admin/users/create_user", data);
  return res.data;
}

// STUDENT (profile)
export async function fetchStudentProfile(studentId: number): Promise<Student> {
  const res = await api.get<Student>(`/student/profile/${studentId}`);
  return res.data;
}

export async function updateStudentProfile(studentId: number, patch: Partial<Student>) {
  const res = await api.put(`/student/profile/${studentId}`, patch);
  return res.data;
}

// TEACHER / STUDENTS LIST
export async function fetchTeacherStudents(): Promise<Student[]> {
  const res = await api.get<Student[]>("/teacher/students");
  return res.data;
}

// ATTENDANCE
export async function checkIn(studentId: number): Promise<AttendanceRecord> {
  const res = await api.post<AttendanceRecord>("/attendance/checkin", {
    StudentId: studentId,
  });
  return res.data;
}

export async function checkOut(attendanceId: number): Promise<AttendanceRecord> {
  const res = await api.put<AttendanceRecord>(`/attendance/checkout/${attendanceId}`);
  return res.data;
}

export async function fetchStudentAttendance(studentId: number): Promise<AttendanceRecord[]> {
  const res = await api.get<AttendanceRecord[]>(`/attendance/student/${studentId}`);
  return res.data;
}

export default api;