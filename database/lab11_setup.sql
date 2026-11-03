INSERT INTO Programming_Language (language_name, version)
VALUES ('Python', '3.12') ON CONFLICT (language_name) DO NOTHING;

INSERT INTO App_User (username, email, password, first_name, last_name, registration_date, preferred_language, profile_bio)
SELECT 'hetpethani', 'hetpethani@example.edu', 'demo-only-change-in-production',
       'Het', 'Pethani', CURRENT_DATE, language_id, 'Lab 11 demo problem author'
FROM Programming_Language WHERE language_name = 'Python'
ON CONFLICT (username) DO NOTHING;