# Job Application Tracker
**Course Project - Advanced Database Management**

## Project Overview
This project is a Full-Stack Database Application designed to track job applications efficiently. The web application leverages a SQL backend, a robust Python API, and an AI-assisted skill matching algorithm. It implements a fully normalized 4-table relational database scheme containing Companies, Jobs, Applications, and Contacts.

## Technologies Used
- **Backend:** Python 3, Flask framework
- **Database:** MySQL relational DB, `mysql-connector-python` layer
- **Frontend:** HTML5, CSS3 with dark mode glassmorphism UI, FontAwesome.
- **GenAI Tooling:** Gemini Pro assist with AI skill matching layout.

## Setup Instructions

### 1. Database Initialization
Ensure you have MySQL installed and running on your local machine.

Open MySQL Workbench and run the scripts found within `schema.sql` to initialize the database:
```sql
SOURCE schema.sql;
```
*(Note: As per project requirements, the tables are already created and seeded with test data via earlier assignments).*

### 2. Configure Environment
Create a `.env` file in the root `job_tracker/` directory matching your MySQL configuration:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=root
DB_DATABASE=job_tracker
DB_PORT=3306
```

### 3. Run the Application
It's recommended to run the app in a Python virtual environment.

```bash
# Create and activate virtual environment (Windows)
python -m venv venv
.\venv\Scripts\activate

# Mac/Linux
# python3 -m venv venv
# source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run the Flask App
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000` to interact with the tracking dashboard.

## Features List
- **Full CRUD operations**: Easily Create, Read, Update, and Delete entries across the Companies, Jobs, Applications, and Contacts database schemas.
- **Data Integrity**: Enforced through foreign key relationships and server-side connection management.
- **Modern User Interface**: A dynamic layout featuring glassmorphism elements, robust hover states, and smooth CSS transitions.
- **GenAI Skill Match**: Compares your raw resume input to JSON-compiled job requirements arrays to compute accurate matching scores, displaying an insightful breakdown.
- **Dynamic Dashboard**: Aggregates essential analytics reflecting the overall status of your job search progress.
