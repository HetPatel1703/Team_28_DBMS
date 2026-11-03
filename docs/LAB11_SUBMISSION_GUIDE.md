# Team 28 - Lab 11 Submission Guide (Option A: Python)

**Project:** LeetCode-Style Practice Management System  
**Main table:** `Problem`  
**Chosen stack:** Python, `psycopg2`, PostgreSQL, Streamlit

## A. Database connectivity code

Capture these code blocks from `db.py` and `db_config.py`:

1. `get_connection()` - shows `psycopg2.connect(**DB_SETTINGS)`.
2. `test_connection()` - shows `SELECT version()`.
3. `db_config.py` - capture the setting names only. Ensure `DB_PASSWORD` is hidden or blank before taking the screenshot.
4. Run the sidebar **Test PostgreSQL connection** button and screenshot the displayed PostgreSQL version.

## B. CRUD operation code and proof

Use `database/crud_reference.sql` for the exact SQL and `db.py` for the matching function. Each mutation returns `cur.rowcount`; Create returns the new generated ID.

| Subsection | SQL/function | Runtime proof to screenshot |
|---|---|---|
| CREATE | `INSERT ...`; `create_problem()` | Fill Add new problem and show `CREATE succeeded: problem #... inserted successfully.` |
| READ | `SELECT ...`; `read_problems()` | Open View problems and show the table plus `READ succeeded: ... record(s) returned.` |
| UPDATE | `UPDATE ... WHERE problem_id = %s`; `update_problem()` | Select a record, modify it, click Save update, and show `UPDATE succeeded: 1 row(s) affected.` |
| DELETE | `DELETE ... WHERE problem_id = %s`; `delete_problem()` | Select a disposable record, check confirmation, delete, and show `DELETE succeeded: 1 row(s) affected.` |

For each subsection place the SQL, the function screenshot, and its runtime screenshot together. Where possible, also show the row in `psql` or pgAdmin.

## C. Frontend screenshots

Capture all three after connecting to your real PostgreSQL database:

1. **Add new problem** tab with the form visible.
2. **View problems** tab with returned table rows.
3. **Update / Delete** tab showing the selected row and deletion confirmation checkbox, or the update success result.

## D. Reflection / conclusion (about 190 words)

> In this lab, we connected the Streamlit user interface for our LeetCode-Style Practice Management System to PostgreSQL using Python and psycopg2. We selected the Problem table because it is a main entity in our system and supports meaningful Create, Read, Update, and Delete actions. One challenge was setting the PostgreSQL connection values correctly and handling an authentication or connection-refused error while the database service was not running. We also had to respect the foreign key from Problem.username to App_User, so our setup script creates a valid demo user before creating a problem. Another important issue was remembering to call conn.commit() after INSERT, UPDATE, and DELETE; without it, a query can appear to succeed but its changes are not saved. We learned that the interface, Python functions, and database form one application pipeline: a Streamlit button sends validated form input to a Python function, the function sends parameterized SQL to PostgreSQL, and the database returns a result that is shown in the interface. We used psycopg2 %s placeholders and a tuple for every input value rather than building SQL strings. This protects the application from SQL injection and also handles text containing quotes correctly. Finally, we kept the password in a private .env file and did not include it in screenshots or submitted code.

## Final PDF order

1. Title page: `Team28_Lab11_DBConnectivity.pdf`.
2. Section A: connection code and version test.
3. Section B: Create, Read, Update, Delete (SQL + function + running proof for each).
4. Section C: three frontend screenshots.
5. Section D: reflection.
