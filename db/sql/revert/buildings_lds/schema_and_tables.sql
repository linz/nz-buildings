-- Revert buildings:buildings_lds/schema_and_tables from pg

BEGIN;

DROP SCHEMA buildings_lds CASCADE;

COMMIT;
