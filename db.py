"""PostgreSQL data access for the CodeTrack practice platform.

All SQL uses psycopg2 placeholders. The functions map directly to the tables
in the supplied Team 28 schema; no external API is required.
"""
from __future__ import annotations

from typing import Any, Iterable
import hashlib
import hmac
import os

import psycopg2
from psycopg2.extras import RealDictCursor

from db_config import DB_SETTINGS


def get_connection():
    return psycopg2.connect(**DB_SETTINGS)


def _rows(sql: str, values: tuple = ()) -> list[dict[str, Any]]:
    with get_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, values)
        return list(cur.fetchall())


def _row(sql: str, values: tuple = ()) -> dict[str, Any] | None:
    result = _rows(sql, values)
    return result[0] if result else None


def _execute(sql: str, values: tuple = ()) -> int:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, values)
        affected = cur.rowcount
        conn.commit()
        return affected


def test_connection() -> str:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT version();")
        return cur.fetchone()[0]


# ---------- Accounts and session ----------

def _password_hash(password: str) -> str:
    """Hashes passwords for new accounts. Old seed rows may be plain classroom data."""
    salt = os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000).hex()
    return "pbkdf2_sha256$" + salt + "$" + digest


def _password_matches(stored: str, supplied: str) -> bool:
    if stored.startswith("pbkdf2_sha256$"):
        _, salt, expected = stored.split("$", 2)
        actual = hashlib.pbkdf2_hmac("sha256", supplied.encode(), salt.encode(), 120_000).hex()
        return hmac.compare_digest(actual, expected)
    return hmac.compare_digest(stored, supplied)


def authenticate(username: str, password: str) -> dict[str, Any] | None:
    user = _row("""SELECT username, password, first_name, last_name, email, profile_bio,
                          preferred_language, account_status
                   FROM App_User WHERE username = %s""", (username.strip(),))
    if not user or user["account_status"] != "Active" or not _password_matches(user["password"], password):
        return None
    _execute("UPDATE App_User SET last_login = CURRENT_TIMESTAMP WHERE username = %s", (user["username"],))
    log_action(user["username"], "LOGIN_SUCCESS", "App_User", user["username"], "Signed in through CodeTrack")
    user.pop("password", None)
    return user


def create_account(username: str, email: str, password: str, first_name: str, last_name: str) -> None:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""INSERT INTO App_User (username, email, password, first_name, last_name)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (username.strip(), email.strip(), _password_hash(password), first_name.strip(), last_name.strip()))
        conn.commit()


def get_profile(username: str) -> dict[str, Any] | None:
    return _row("""SELECT u.username, u.email, u.first_name, u.last_name, u.profile_bio,
                          u.registration_date, u.last_login, pl.language_name AS preferred_language
                   FROM App_User u LEFT JOIN Programming_Language pl ON pl.language_id = u.preferred_language
                   WHERE u.username = %s""", (username,))


def update_profile(username: str, email: str, bio: str, language_id: int | None) -> None:
    _execute("""UPDATE App_User SET email = %s, profile_bio = %s, preferred_language = %s
                WHERE username = %s""", (email.strip(), bio.strip() or None, language_id, username))
    log_action(username, "UPDATE_PROFILE", "App_User", username, "Updated profile details")


def user_is_admin(username: str) -> bool:
    return bool(_row("""SELECT 1 FROM User_Role ur JOIN Role r ON r.role_id = ur.role_id
                         WHERE ur.username = %s AND r.role_name IN ('Administrator', 'Problem Setter')
                         AND (ur.end_at IS NULL OR ur.end_at > CURRENT_TIMESTAMP)""", (username,)))


def languages() -> list[dict[str, Any]]:
    return _rows("SELECT language_id, language_name, version FROM Programming_Language ORDER BY language_name")


def log_action(username: str, action: str, entity_type: str, entity_id: str | None, details: str) -> None:
    _execute("""INSERT INTO Audit_Log (username, action_type, entity_type, entity_id, action_details)
                VALUES (%s, %s, %s, %s, %s)""", (username, action, entity_type, entity_id, details))


# ---------- Problems, topics and submissions ----------

def topics() -> list[dict[str, Any]]:
    return _rows("SELECT topic_id, topic_name, description FROM Topic ORDER BY topic_name")


def problem_list(username: str, search: str = "", difficulties: Iterable[str] = (), topic_id: int | None = None,
                 state: str = "All") -> list[dict[str, Any]]:
    where, values = ["LOWER(p.title) LIKE LOWER(%s)"], ["%" + search.strip() + "%"]
    selected = list(difficulties)
    if selected:
        where.append("p.difficulty_name = ANY(%s)")
        values.append(selected)
    if topic_id:
        where.append("EXISTS (SELECT 1 FROM Problem_Topic filter_pt WHERE filter_pt.problem_id = p.problem_id AND filter_pt.topic_id = %s)")
        values.append(topic_id)
    if state == "Solved":
        where.append("up.progress_status = 'Solved'")
    elif state == "Attempted":
        where.append("up.progress_status = 'Attempted'")
    elif state == "Unsolved":
        where.append("(up.progress_status IS NULL OR up.progress_status <> 'Solved')")
    sql = """SELECT p.problem_id, p.title, p.difficulty_name, p.username AS author,
                    COALESCE(up.progress_status, 'Not started') AS progress_status,
                    COALESCE(STRING_AGG(DISTINCT t.topic_name, ', '), 'General') AS topics,
                    COUNT(DISTINCT s.submission_id) AS submissions
             FROM Problem p
             LEFT JOIN User_Progress up ON up.problem_id = p.problem_id AND up.username = %s
             LEFT JOIN Problem_Topic pt ON pt.problem_id = p.problem_id
             LEFT JOIN Topic t ON t.topic_id = pt.topic_id
             LEFT JOIN Submission s ON s.problem_id = p.problem_id
             WHERE """ + " AND ".join(where) + """
             GROUP BY p.problem_id, p.title, p.difficulty_name, p.username, up.progress_status
             ORDER BY p.problem_id DESC"""
    return _rows(sql, (username, *values))


def problem_detail(problem_id: int) -> dict[str, Any] | None:
    problem = _row("""SELECT p.*, COALESCE(STRING_AGG(DISTINCT t.topic_name, ', '), 'General') AS topics
                       FROM Problem p LEFT JOIN Problem_Topic pt ON pt.problem_id = p.problem_id
                       LEFT JOIN Topic t ON t.topic_id = pt.topic_id WHERE p.problem_id = %s
                       GROUP BY p.problem_id""", (problem_id,))
    if not problem:
        return None
    problem["constraints"] = _rows("""SELECT constraint_id, constraint_description FROM Problem_Constraint
                                       WHERE problem_id = %s ORDER BY constraint_id""", (problem_id,))
    problem["test_cases"] = _rows("""SELECT test_case_id, input_data, expected_output, is_sample FROM Test_Case
                                      WHERE problem_id = %s ORDER BY test_case_id""", (problem_id,))
    return problem


def create_problem(title: str, description: str, difficulty: str, username: str, topic_ids: list[int],
                   constraints: list[str], samples: list[tuple[str, str]]) -> int:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""INSERT INTO Problem (title, description, difficulty_name, username, published_at)
                       VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP) RETURNING problem_id""",
                    (title.strip(), description.strip(), difficulty, username))
        problem_id = cur.fetchone()[0]
        for topic_id in topic_ids:
            cur.execute("INSERT INTO Problem_Topic (problem_id, topic_id) VALUES (%s, %s)", (problem_id, topic_id))
        for number, item in enumerate((c for c in constraints if c.strip()), 1):
            cur.execute("""INSERT INTO Problem_Constraint (problem_id, constraint_id, constraint_description)
                           VALUES (%s, %s, %s)""", (problem_id, number, item.strip()))
        for number, (input_data, expected_output) in enumerate(samples, 1):
            if input_data.strip() or expected_output.strip():
                cur.execute("""INSERT INTO Test_Case (problem_id, test_case_id, input_data, expected_output, is_sample)
                               VALUES (%s, %s, %s, %s, TRUE)""", (problem_id, number, input_data.strip(), expected_output.strip()))
        conn.commit()
    log_action(username, "CREATE_PROBLEM", "Problem", str(problem_id), "Created " + title.strip())
    return problem_id


def submit_solution(username: str, problem_id: int, language_id: int, code: str, verdict: str) -> int:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""INSERT INTO Submission (username, problem_id, language_id, submitted_code, verdict,
                                                  execution_time, memory_used)
                       VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING submission_id""",
                    (username, problem_id, language_id, code, verdict,
                     0.012 if verdict == "Accepted" else None, 8.4 if verdict == "Accepted" else None))
        submission_id = cur.fetchone()[0]
        status = "Solved" if verdict == "Accepted" else "Attempted"
        score = 100 if verdict == "Accepted" else 0
        cur.execute("""INSERT INTO User_Progress (username, problem_id, progress_status, solved_time, attempt_count, best_score)
                       VALUES (%s, %s, %s, CASE WHEN %s = 'Solved' THEN CURRENT_TIMESTAMP END, 1, %s)
                       ON CONFLICT (username, problem_id) DO UPDATE SET
                         progress_status = CASE WHEN EXCLUDED.progress_status = 'Solved' THEN 'Solved'
                                                ELSE User_Progress.progress_status END,
                         solved_time = CASE WHEN EXCLUDED.progress_status = 'Solved' THEN CURRENT_TIMESTAMP
                                            ELSE User_Progress.solved_time END,
                         attempt_count = User_Progress.attempt_count + 1,
                         best_score = GREATEST(User_Progress.best_score, EXCLUDED.best_score)""",
                    (username, problem_id, status, status, score))
        conn.commit()
    log_action(username, "SUBMIT_CODE", "Submission", str(submission_id), verdict + " for problem " + str(problem_id))
    return submission_id


def recent_submissions(username: str, limit: int = 10) -> list[dict[str, Any]]:
    return _rows("""SELECT s.submission_id, p.title, pl.language_name, s.verdict, s.submission_time,
                         s.execution_time, s.memory_used FROM Submission s
                  JOIN Problem p ON p.problem_id = s.problem_id
                  JOIN Programming_Language pl ON pl.language_id = s.language_id
                  WHERE s.username = %s ORDER BY s.submission_time DESC LIMIT %s""", (username, limit))

def update_problem(problem_id: int, title: str, description: str, difficulty: str) -> int:
    sql = """
        UPDATE Problem
        SET title = %s, description = %s, difficulty_name = %s, updated_at = CURRENT_TIMESTAMP
        WHERE problem_id = %s
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (title.strip(), description.strip(), difficulty, problem_id))
        affected = cur.rowcount
        conn.commit()
        return affected

def delete_problem(problem_id: int) -> int:
    sql = "DELETE FROM Problem WHERE problem_id = %s"
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (problem_id,))
        affected = cur.rowcount
        conn.commit()
        return affected


# ---------- Profiles, leaderboard, contests, community ----------

def dashboard_stats(username: str) -> dict[str, Any]:
    return _row("""SELECT COUNT(*) FILTER (WHERE progress_status = 'Solved') AS solved,
                         COUNT(*) FILTER (WHERE progress_status = 'Attempted') AS attempted,
                         COALESCE(SUM(best_score), 0) AS score,
                         (SELECT COUNT(*) FROM Submission WHERE username = %s) AS submissions
                  FROM User_Progress WHERE username = %s""", (username, username)) or {}


def difficulty_breakdown(username: str) -> list[dict[str, Any]]:
    return _rows("""SELECT p.difficulty_name, COUNT(*) AS solved FROM User_Progress up
                  JOIN Problem p ON p.problem_id = up.problem_id
                  WHERE up.username = %s AND up.progress_status = 'Solved'
                  GROUP BY p.difficulty_name ORDER BY p.difficulty_name""", (username,))


def badges_for(username: str) -> list[dict[str, Any]]:
    return _rows("""SELECT b.badge_name, b.badge_type, b.badge_criteria, ub.earned_at FROM User_Badge ub
                  JOIN Badge b ON b.badge_id = ub.badge_id WHERE ub.username = %s ORDER BY ub.earned_at DESC""", (username,))


def leaderboard() -> list[dict[str, Any]]:
    return _rows("""WITH problem_scores AS (SELECT username, COALESCE(SUM(best_score), 0) AS score
                                             FROM User_Progress WHERE progress_status = 'Solved' GROUP BY username),
                       contest_scores AS (SELECT username, COALESCE(SUM(total_score), 0) AS score
                                          FROM Contest_Participant GROUP BY username)
                  SELECT u.username, u.first_name || ' ' || u.last_name AS name,
                         COALESCE(ps.score, 0) AS problem_score, COALESCE(cs.score, 0) AS contest_score,
                         COALESCE(ps.score, 0) + COALESCE(cs.score, 0) AS global_score
                  FROM App_User u LEFT JOIN problem_scores ps ON ps.username = u.username
                  LEFT JOIN contest_scores cs ON cs.username = u.username
                  WHERE u.account_status = 'Active' ORDER BY global_score DESC, u.username LIMIT 50""")


def contests(username: str) -> list[dict[str, Any]]:
    return _rows("""SELECT c.*, cp.completion_status, cp.total_score, cp.contest_rank,
                         EXISTS (SELECT 1 FROM Contest_Participant x WHERE x.contest_id = c.contest_id AND x.username = %s) AS registered,
                         COUNT(cpr.problem_id) AS problem_count
                  FROM Contest c LEFT JOIN Contest_Participant cp ON cp.contest_id = c.contest_id AND cp.username = %s
                  LEFT JOIN Contest_Problem cpr ON cpr.contest_id = c.contest_id
                  GROUP BY c.contest_id, cp.completion_status, cp.total_score, cp.contest_rank
                  ORDER BY c.start_time DESC""", (username, username))


def contest_problems(contest_id: int) -> list[dict[str, Any]]:
    return _rows("""SELECT cp.problem_order, cp.points, p.problem_id, p.title, p.difficulty_name
                  FROM Contest_Problem cp JOIN Problem p ON p.problem_id = cp.problem_id
                  WHERE cp.contest_id = %s ORDER BY cp.problem_order""", (contest_id,))


def register_for_contest(username: str, contest_id: int) -> bool:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""INSERT INTO Contest_Participant (username, contest_id) VALUES (%s, %s)
                       ON CONFLICT (username, contest_id) DO NOTHING""", (username, contest_id))
        changed = cur.rowcount == 1
        conn.commit()
    if changed:
        log_action(username, "REGISTER_CONTEST", "Contest", str(contest_id), "Registered through CodeTrack")
    return changed


def discussions(problem_id: int | None = None) -> list[dict[str, Any]]:
    sql, values = """SELECT d.discussion_id, d.discussion_title, d.content, d.username, p.title AS problem_title,
                           COUNT(c.comment_id) AS comments FROM Discussion d JOIN Problem p ON p.problem_id = d.problem_id
                    LEFT JOIN Comment c ON c.discussion_id = d.discussion_id""", []
    if problem_id:
        sql += " WHERE d.problem_id = %s"
        values.append(problem_id)
    sql += " GROUP BY d.discussion_id, p.title ORDER BY d.discussion_id DESC"
    return _rows(sql, tuple(values))


def create_discussion(username: str, problem_id: int, title: str, content: str) -> int:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""INSERT INTO Discussion (problem_id, username, discussion_title, content)
                       VALUES (%s, %s, %s, %s) RETURNING discussion_id""", (problem_id, username, title.strip(), content.strip()))
        discussion_id = cur.fetchone()[0]
        conn.commit()
    log_action(username, "CREATE_DISCUSSION", "Discussion", str(discussion_id), title.strip())
    return discussion_id


def comments(discussion_id: int) -> list[dict[str, Any]]:
    return _rows("SELECT comment_id, username, comment_text FROM Comment WHERE discussion_id = %s ORDER BY comment_id", (discussion_id,))


def create_comment(username: str, discussion_id: int, text: str) -> None:
    _execute("INSERT INTO Comment (discussion_id, username, comment_text) VALUES (%s, %s, %s)",
             (discussion_id, username, text.strip()))
