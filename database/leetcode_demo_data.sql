-- Optional starter data for the full CodeTrack UI.
-- Run this after 28_DDL.sql. It can be run again safely.
-- Demo accounts: team28_admin / code123 (Admin), demo_user / code123 (User)

INSERT INTO Programming_Language (language_name, version) VALUES
  ('Python', '3.12'), ('Java', '21'), ('C++', '17'), ('JavaScript', 'ES2023')
ON CONFLICT (language_name) DO NOTHING;

INSERT INTO App_User (username, email, password, first_name, last_name, preferred_language, profile_bio) VALUES
  ('team28_admin', 'team28_admin@example.edu', 'code123', 'Team', 'TwentyEight',
   (SELECT language_id FROM Programming_Language WHERE language_name = 'Python'),
   'Problem setter and platform administrator.'),
  ('demo_user', 'demo_user@example.edu', 'code123', 'Demo', 'Coder',
   (SELECT language_id FROM Programming_Language WHERE language_name = 'Java'),
   'Learning data structures one problem at a time.')
ON CONFLICT (username) DO NOTHING;

-- Ensures the documented demo password works even if the earlier Lab 11 seed
-- script created team28_admin first.
UPDATE App_User SET password = 'code123'
WHERE username IN ('team28_admin', 'demo_user');

INSERT INTO Role (role_name) VALUES ('Admin'), ('Problem Setter'), ('User')
ON CONFLICT (role_name) DO NOTHING;

INSERT INTO User_Role (username, role_id)
SELECT 'team28_admin', role_id FROM Role WHERE role_name = 'Admin'
ON CONFLICT (username, role_id) DO NOTHING;

INSERT INTO User_Role (username, role_id)
SELECT 'demo_user', role_id FROM Role WHERE role_name = 'User'
ON CONFLICT (username, role_id) DO NOTHING;

INSERT INTO Topic (topic_name, description) VALUES
  ('Array', 'Indexed collections and two-pointer patterns.'),
  ('Hash Table', 'Fast lookup and frequency counting.'),
  ('Linked List', 'Pointer manipulation and traversal.'),
  ('Dynamic Programming', 'Optimal substructure and memoization.'),
  ('Graph', 'Traversal, paths, and connectivity.')
ON CONFLICT (topic_name) DO NOTHING;

INSERT INTO Badge (badge_name, badge_criteria, badge_type) VALUES
  ('First Accepted', 'Solve one problem.', 'Achievement'),
  ('Practice Starter', 'Submit five solutions.', 'Milestone'),
  ('Contest Ready', 'Register for a contest.', 'Special')
ON CONFLICT (badge_name) DO NOTHING;

INSERT INTO Problem (title, description, difficulty_name, username, published_at) VALUES
  ('Two Sum', 'Given an array of integers nums and an integer target, return the indices of two numbers that add up to target. You may assume exactly one solution exists.', 'Easy', 'team28_admin', CURRENT_TIMESTAMP),
  ('Valid Parentheses', 'Given a string containing parentheses, determine whether the input string is valid. Open brackets must be closed by the same type of brackets in the correct order.', 'Easy', 'team28_admin', CURRENT_TIMESTAMP),
  ('Longest Increasing Subsequence', 'Given an integer array nums, return the length of the longest strictly increasing subsequence.', 'Medium', 'team28_admin', CURRENT_TIMESTAMP)
ON CONFLICT (title) DO NOTHING;

INSERT INTO Problem_Topic (problem_id, topic_id)
SELECT p.problem_id, t.topic_id FROM Problem p CROSS JOIN Topic t
WHERE (p.title = 'Two Sum' AND t.topic_name IN ('Array', 'Hash Table'))
   OR (p.title = 'Valid Parentheses' AND t.topic_name IN ('Hash Table'))
   OR (p.title = 'Longest Increasing Subsequence' AND t.topic_name IN ('Dynamic Programming', 'Array'))
ON CONFLICT (problem_id, topic_id) DO NOTHING;

INSERT INTO Problem_Constraint (problem_id, constraint_id, constraint_description)
SELECT problem_id, 1, '2 <= nums.length <= 10^4' FROM Problem WHERE title = 'Two Sum'
ON CONFLICT (problem_id, constraint_id) DO NOTHING;

INSERT INTO Test_Case (problem_id, test_case_id, input_data, expected_output, is_sample)
SELECT problem_id, 1, 'nums = [2,7,11,15], target = 9', '[0,1]', TRUE FROM Problem WHERE title = 'Two Sum'
ON CONFLICT (problem_id, test_case_id) DO NOTHING;

INSERT INTO Contest (contest_name, description, start_time, end_time, contest_status, scoring_rule)
SELECT 'CodeTrack Weekly #1', 'A short weekly contest for practice.', CURRENT_TIMESTAMP + INTERVAL '2 days',
       CURRENT_TIMESTAMP + INTERVAL '2 days 2 hours', 'Upcoming', 'ICPC'
WHERE NOT EXISTS (SELECT 1 FROM Contest WHERE contest_name = 'CodeTrack Weekly #1');

INSERT INTO Contest_Problem (contest_id, problem_id, problem_order, points)
SELECT c.contest_id, p.problem_id,
       CASE p.title WHEN 'Two Sum' THEN 1 WHEN 'Valid Parentheses' THEN 2 ELSE 3 END,
       CASE p.difficulty_name WHEN 'Easy' THEN 100 ELSE 200 END
FROM Contest c JOIN Problem p ON p.title IN ('Two Sum', 'Valid Parentheses', 'Longest Increasing Subsequence')
WHERE c.contest_name = 'CodeTrack Weekly #1'
ON CONFLICT (contest_id, problem_id) DO NOTHING;

INSERT INTO Discussion (problem_id, username, discussion_title, content)
SELECT p.problem_id, 'team28_admin', 'Welcome to Two Sum', 'Share your approach without posting the complete solution immediately.'
FROM Problem p WHERE p.title = 'Two Sum'
  AND NOT EXISTS (SELECT 1 FROM Discussion d WHERE d.discussion_title = 'Welcome to Two Sum');
