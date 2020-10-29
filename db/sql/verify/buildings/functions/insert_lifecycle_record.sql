-- Verify nz-buildings:buildings/functions/insert_lifecycle_record on pg

BEGIN;

SELECT has_function_privilege('buildings.lifecycle_insert_record(integer, integer)', 'execute');

ROLLBACK;
