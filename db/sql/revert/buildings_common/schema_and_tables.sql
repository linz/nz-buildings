-- Revert buildings:buildings_common/schema_and_tables from pg

BEGIN;

DROP SCHEMA buildings_common CASCADE;

COMMIT;
