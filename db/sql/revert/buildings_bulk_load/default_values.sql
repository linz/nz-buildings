-- Revert nz-buildings:buildings_bulk_load/default_values from pg

BEGIN;

TRUNCATE buildings_bulk_load.organisation CASCADE;

TRUNCATE buildings_bulk_load.bulk_load_status CASCADE;

TRUNCATE buildings_bulk_load.qa_status CASCADE;

COMMIT;
