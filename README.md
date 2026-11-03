<div align="center">

# ⚡ CodeTrack 
### LeetCode-Style Practice Management System
**Team 28 DBMS Project**

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)

*A robust, database-driven platform for coding practice, competitive programming, and community discussion.*

</div>

---

## 📖 Overview

**CodeTrack** is a comprehensive Python, PostgreSQL, and Streamlit application designed as a LeetCode-style Practice Management System. It serves as the frontend interface mapped directly to the **Team 28 Database Schema**, allowing users to practice problems, track their progress, participate in contests, and engage with a community. 

> **Note:** This project is heavily database-driven. All SQL queries use secure `psycopg2` placeholders mapping directly to the underlying PostgreSQL schema without the need for an external API.

---

## ✨ Key Features

### 👨‍💻 For Users
- **Secure Authentication:** Sign up and log in with securely hashed passwords.
- **Personalized Dashboard:** View solved counts, total attempts, practice scores, and recent submissions.
- **Advanced Problemset Filtering:** Search and filter problems by keywords, difficulty (`Easy`, `Medium`, `Hard`), topic, and completion status.
- **Interactive Solve Environment:** Read problem constraints, view sample test cases, and submit code. *(Includes a simulated judge verdict selector for demo purposes).*
- **Contest Management:** Browse upcoming contests, register, and view included contest problems.
- **Global Leaderboard:** Compete with peers ranked by solved-problem scores and contest performance.
- **Community Discussions:** Ask questions, share approaches, and comment on specific problems.
- **Rich Profiles:** Track your difficulty breakdown (visualized via charts), view earned badges, and set language preferences.

### 🛡️ For Administrators (Admin Studio)
- **Problem Management:** Create, publish, update, and delete coding problems.
- **Rich Constraints & Test Cases:** Add detailed constraints and sample input/output test cases directly to the database.

---

## 🛠️ Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | Streamlit | Responsive, custom-styled UI with dark/light mode optimization. |
| **Backend** | Python | Core logic, routing, and database communication. |
| **Database** | PostgreSQL | Relational database handling all users, problems, submissions, and contests. |
| **Driver** | `psycopg2` | PostgreSQL database adapter for Python. |
| **Security** | `hashlib` & `hmac` | Secure password hashing (PBKDF2-HMAC-SHA256). |

---

## 🚀 Installation & Setup

Follow these steps to get CodeTrack running on your local machine.

### 1. Database Configuration
1. Install PostgreSQL and create a new database named `Team_28_DBMS` (or your preferred name).
2. Run the supplied DDL script (`28_DDL.sql`) to generate the tables.
3. Run the demo data script (`database/leetcode_demo_data.sql`) to populate initial topics, languages, and sample data.

### 2. Project Setup
Clone the repository and set up your Python environment:

```bash
# Clone the repository
git clone https://github.com/HetPatel1703/Team_28_DBMS.git
cd Team_28_DBMS

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory and add your PostgreSQL credentials:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=Team_28_DBMS
DB_USER=your_postgres_username
DB_PASSWORD=your_postgres_password
```

### 4. Run the Application
Launch the Streamlit app:

```bash
streamlit run app.py
```

---

## 🔐 Demo Credentials

Use the following accounts to test the application immediately after populating the demo data:

| Role | Username | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Admin** | `team28_admin` | `code123` | Full platform access + Admin Studio (CRUD problems) |
| **User** | `demo_user` | `code123` | Standard user-facing platform pages |

> ⚠️ **Warning:** These are demo accounts. Please change or delete them before deploying to a production environment. **Never commit your `.env` file to version control.**

---

## 🛡️ Database Safety & Architecture

- **SQL Injection Prevention:** All user inputs are sanitized using `psycopg2` parameter placeholders. The application strictly avoids string concatenation in SQL queries.
- **Authentication:** Passwords for newly created accounts are salted and hashed using `pbkdf2_sha256`. 
- **Audit Logging:** Crucial actions (logins, profile updates, problem creation, and code submissions) are tracked in the database's `Audit_Log` table.

---
<div align="center">
  <i>Developed with ❤️ by Team 28</i>
</div>