-- Lab 11 exact SQL statements for the Python Option A implementation.
-- User values are supplied as a tuple to psycopg2, never joined into SQL text.

-- CREATE: db.create_problem(...)
INSERT INTO Problem (title, description, difficulty_name, username, published_at)
VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
RETURNING problem_id;

-- READ: db.read_problems(...)
SELECT problem_id, title, description, difficulty_name, username, created_at, updated_at
FROM Problem
WHERE LOWER(title) LIKE LOWER(%s)
ORDER BY problem_id DESC;

-- UPDATE: db.update_problem(...)
UPDATE Problem
SET title = %s, description = %s, difficulty_name = %s, username = %s,
    updated_at = CURRENT_TIMESTAMP
WHERE problem_id = %s;

-- DELETE: db.delete_problem(...)
DELETE FROM Problem
WHERE problem_id = %s;
