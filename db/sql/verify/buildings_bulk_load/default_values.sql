-- Verify nz-buildings:buildings_bulk_load/default_values on pg

BEGIN;

SELECT 1/count(*)
FROM buildings_bulk_load.organisation;

SELECT 1/count(*)
FROM buildings_bulk_load.bulk_load_status;

SELECT 1/count(*)
FROM buildings_bulk_load.qa_status;

ROLLBACK;
