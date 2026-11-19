-- =========================================================
-- fix_sequences.sql
-- Run this once after loading demo data that used explicit ids.
-- It safely moves every SERIAL/BIGSERIAL sequence above MAX(id).
-- Safe to re-run at any time.
-- =========================================================

SELECT setval(pg_get_serial_sequence('problem',              'problem_id'),
              COALESCE((SELECT MAX(problem_id)  FROM Problem),              0) + 1, false);

SELECT setval(pg_get_serial_sequence('submission',           'submission_id'),
              COALESCE((SELECT MAX(submission_id) FROM Submission),         0) + 1, false);

SELECT setval(pg_get_serial_sequence('submission_result',    'result_id'),
              COALESCE((SELECT MAX(result_id)   FROM Submission_Result),    0) + 1, false);

SELECT setval(pg_get_serial_sequence('user_progress',        'progress_id'),
              COALESCE((SELECT MAX(progress_id) FROM User_Progress),        0) + 1, false);

SELECT setval(pg_get_serial_sequence('contest',              'contest_id'),
              COALESCE((SELECT MAX(contest_id)  FROM Contest),              0) + 1, false);

SELECT setval(pg_get_serial_sequence('user_rating_history',  'rating_id'),
              COALESCE((SELECT MAX(rating_id)   FROM User_Rating_History),  0) + 1, false);

SELECT setval(pg_get_serial_sequence('discussion',           'discussion_id'),
              COALESCE((SELECT MAX(discussion_id) FROM Discussion),         0) + 1, false);

SELECT setval(pg_get_serial_sequence('comment',              'comment_id'),
              COALESCE((SELECT MAX(comment_id)  FROM Comment),              0) + 1, false);

SELECT setval(pg_get_serial_sequence('badge',                'badge_id'),
              COALESCE((SELECT MAX(badge_id)    FROM Badge),                0) + 1, false);

SELECT setval(pg_get_serial_sequence('audit_log',            'log_id'),
              COALESCE((SELECT MAX(log_id)      FROM Audit_Log),            0) + 1, false);

SELECT setval(pg_get_serial_sequence('problem_review',       'review_id'),
              COALESCE((SELECT MAX(review_id)   FROM Problem_Review),       0) + 1, false);

SELECT setval(pg_get_serial_sequence('topic',                'topic_id'),
              COALESCE((SELECT MAX(topic_id)    FROM Topic),                0) + 1, false);

SELECT setval(pg_get_serial_sequence('role',                 'role_id'),
              COALESCE((SELECT MAX(role_id)     FROM Role),                 0) + 1, false);

SELECT setval(pg_get_serial_sequence('permission',           'permission_id'),
              COALESCE((SELECT MAX(permission_id) FROM Permission),         0) + 1, false);

SELECT setval(pg_get_serial_sequence('programming_language', 'language_id'),
              COALESCE((SELECT MAX(language_id) FROM Programming_Language), 0) + 1, false);