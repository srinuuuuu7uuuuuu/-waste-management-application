# Smart Waste Management System

A Flask-based Smart Waste Management System that allows users to report waste issues, upload images, and track waste collection status. The system also includes an admin dashboard for managing reports and updating collection status.

---

## 🚀 Features

- User Registration & Login Authentication
- Secure Password Hashing
- Waste Reporting System
- Upload Waste Images
- User Dashboard
- Admin Dashboard
- Waste Collection Status Tracking
- Weekly Collection Target Progress
- SQLite Database Integration
- Responsive Web Interface

---

## 🛠️ Tech Stack

### Frontend
- HTML
- CSS
- Bootstrap (optional)

### Backend
- Python
- Flask

### Database
- SQLite
- SQLAlchemy ORM

### Authentication
- Flask-Login
- Werkzeug Security

---

## 📂 Project Structure

```bash
smart_waste_management/
│
├── app.py
├── models.py
├── waste_management_v2.db
│
├── templates/
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   └── report.html
│
├── static/
│   └── uploads/
│
└── README.md