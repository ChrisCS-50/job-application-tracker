<div align="center">
  <img src="https://img.shields.io/badge/FIU-Navy_&_Gold-081E3F?style=for-the-badge&logoColor=CC8A00" alt="FIU Theme" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL" />
  
  <h1>JobTracker Pro: Enterprise Application Management</h1>
  <p><em>Advanced Database Management Course Project</em></p>
</div>

---

## Project Overview

JobTracker Pro is a Full-Stack Database Application designed to meticulously track the job hunting lifecycle. Built with a robust **Python/Flask** backend and a fully normalized **MySQL** relational database, the platform leverages dynamic SQL queries and parameterization for uncompromising data integrity. 

This build integrates **Florida International University (FIU)** brand aesthetics (Navy `#081E3F` & Gold `#CC8A00`) alongside modern Enterprise SaaS design principles, offering both Light and Dark mode experiences.

## Key Features

- **Full Data Lifecycles (CRUD)**: Create, Read, Update, and Delete entries across 4 relational schemas: *Companies*, *Jobs*, *Applications*, and *Contacts*.
- **AI Skill Matching Engine**: Compares applicant resumes against JSON-compiled job requirement arrays to calculate compatibility percentages and expose skill gaps.
- **Enterprise UI/UX**: High-contrast tables, interactive data filtering, and a seamless `localStorage` persistent Light/Dark mode toggle switch.
- **Analytical Dashboard**: Features a `Chart.js` powered doughnut funnel visualizing your success rate (Offers vs. Interviews vs. Rejections).
- **Data Integrity**: Enforced via cascading SQL foreign keys and prepared statements protecting against SQL injection.

## System Architecture

```text
job_tracker/
├── app.py                 # Flask server & route controllers
├── database.py            # MySQL Database Abstraction Layer
├── schema.sql             # Relational Table Definitions
├── requirements.txt       # Python Dependencies
├── static/
│   └── style.css          # FIU Themed CSS Variables & Styling
└── templates/
    ├── base.html          # Jinja2 Master Layout & JS toggles
    ├── dashboard.html     # Analytics & Chart.js funnel
    ├── companies.html     # Component Tables...
    └── ...
```

## Quick Setup Guide

### 1. Database Initialization
Ensure **MySQL Workbench** or a local MySQL server is running on port `3306`.
Execute the schema script to provision the constraints:
```sql
SOURCE schema.sql;
```
*(Note: As per assignment prerequisites, the tables are already initialized/seeded in the `job_tracker` database).*

### 2. Environment Configuration
Copy the provided template and fill in **your own** database credentials:
```bash
cp .env.example .env
```
Then edit `.env` with your values:
```env
DB_HOST=localhost
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_DATABASE=job_tracker
DB_PORT=3306
```
> **Never commit your `.env` file.** It is already listed in `.gitignore`. The `.env.example` file (with placeholder values) is provided for reference only.

### 3. Server Initialization
It is highly recommended to run this server isolated within a Python virtual environment.

```bash
# 1. Create and isolate environment
python -m venv venv
.\venv\Scripts\activate   # Windows
# source venv/bin/activate # Mac/Linux

# 2. Install core dependencies
pip install -r requirements.txt

# 3. Ignite the server
python app.py
```
**Access the platform securely at:** `http://127.0.0.1:5000`

---
<div align="center">
  <em>Tested End-to-End Successfully</em>
</div>