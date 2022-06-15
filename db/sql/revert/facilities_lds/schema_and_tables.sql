-- Revert nz-buildings:facilities_lds/schema_and_tables from pg

BEGIN;

DROP SCHEMA facilities_lds  CASCADE;

COMMIT;
