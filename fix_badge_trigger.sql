-- =========================================================
-- fix_badge_trigger.sql
--
-- Fixes:
--   insert or update on table "user_badge" violates foreign
--   key constraint "fk_user_badge_badge"
--   DETAIL: Key (badge_id)=(30) is not present in table "badge"
--
-- Two-part fix:
--   1. Guarantee the "First Blood" badge row exists (by name,
--      independent of whatever SERIAL id it receives).
--   2. Replace award_first_blood() so it looks the badge up
--      by name and is idempotent — never fails on re-award.
-- =========================================================

BEGIN;

-- (1) Ensure the badge row exists ------------------------------------
INSERT INTO Badge (badge_name, badge_criteria, badge_type)
VALUES ('First Blood', 'First user to solve a problem', 'Achievement')
ON CONFLICT (badge_name) DO NOTHING;

-- (2) Rewrite the trigger function to use the badge name -------------
CREATE OR REPLACE FUNCTION award_first_blood() RETURNS TRIGGER AS $$
DECLARE
    v_badge_id INTEGER;
BEGIN
    SELECT badge_id
      INTO v_badge_id
      FROM Badge
     WHERE badge_name = 'First Blood';

    -- If the badge catalog was wiped, don't break the user's submission
    IF v_badge_id IS NOT NULL THEN
        INSERT INTO User_Badge (username, badge_id, earned_at)
        VALUES (NEW.username, v_badge_id, CURRENT_TIMESTAMP)
        ON CONFLICT (username, badge_id) DO NOTHING;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMIT;