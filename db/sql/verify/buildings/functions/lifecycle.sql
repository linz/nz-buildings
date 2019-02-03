-- Verify buildings:buildings/functions/lifecycle on pg

BEGIN;

SELECT has_function_privilege('buildings.lifecycle_add_record(integer, integer)', 'execute');

ROLLBACK;
