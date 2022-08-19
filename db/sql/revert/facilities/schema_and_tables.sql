-- Revert nz-buildings:facilities/schema_and_tables from pg

BEGIN;

DROP SCHEMA facilities CASCADE;

COMMIT;
