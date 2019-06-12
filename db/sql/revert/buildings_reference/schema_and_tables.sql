-- Revert nz-buildings:buildings_reference/schema_and_tables from pg

BEGIN;

DROP SCHEMA buildings_reference CASCADE;

COMMIT;
