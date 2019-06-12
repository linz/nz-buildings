-- Revert nz-buildings:buildings_bulk_load/schema_and_tables from pg

BEGIN;

DROP SCHEMA buildings_bulk_load CASCADE;

COMMIT;
