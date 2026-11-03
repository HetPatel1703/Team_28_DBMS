# CodeTrack - LeetCode-Style Practice Platform

CodeTrack is Team 28's Python, PostgreSQL, and Streamlit application for the
LeetCode-Style Practice Management System. It is connected only to tables in
the supplied database schema.

## Included features

- Account registration and sign in
- Dashboard with solved count, practice score, and recent submissions
- Problemset with keyword, difficulty, topic, and status filters
- Problem detail with constraints and sample test cases
- Solution submission history and progress tracking
- Contest listing, registration, and contest problem lists
- Global leaderboard
- Discussions and comments
- Profile, language preference, difficulty chart, and badges
- Admin Studio for publishing problems with topics, constraints, and samples

The Solve page records a real submission and updates progress. The schema does
not include a secure compiler or execution sandbox, so its labelled demo
verdict selector records a simulated judge result rather than running code.

## First-time setup

1. Create the PostgreSQL database named leetcode_practice.
2. Run the supplied 28_DDL.sql file in that database.
3. Run database/leetcode_demo_data.sql in the same database.
4. Copy .env.example to .env and put your real PostgreSQL password there.
5. Create a virtual environment, install requirements.txt, and start Streamlit:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    streamlit run app.py

## Demo sign-in

| Username | Password | Access |
| --- | --- | --- |
| team28_admin | code123 | Full platform and Admin Studio |
| demo_user | code123 | User-facing platform pages |

These are demo accounts only. Change or delete them before deploying the
project beyond your course environment. Never upload your .env file.

## Database safety

All user values use psycopg2 placeholders. The application does not join user
input into SQL text. New account passwords are salted and hashed; the supplied
demo rows retain plain passwords only so the classroom setup is simple.
