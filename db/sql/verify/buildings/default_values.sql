-- Verify nz-buildings:buildings/default_values on pg

BEGIN;

SELECT 1/count(*)
FROM buildings.lifecycle_stage;

SELECT 1/count(*)
FROM buildings.use;

ROLLBACK;
