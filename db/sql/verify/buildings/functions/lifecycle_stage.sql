-- Verify nz-buildings:buildings/functions/lifecycle_stage on pg

BEGIN;

SELECT has_function_privilege('buildings.lifecycle_stage_insert(varchar(40))', 'execute');

ROLLBACK;
