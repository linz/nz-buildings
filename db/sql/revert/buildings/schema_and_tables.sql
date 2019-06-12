-- Revert nz-buildings:buildings/schema_and_tables from pg

BEGIN;

DROP SCHEMA buildings CASCADE;

COMMIT;
