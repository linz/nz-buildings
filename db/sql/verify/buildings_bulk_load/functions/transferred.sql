-- Verify buildings:buildings_bulk_load/functions/transferred on pg

BEGIN;

SELECT has_function_privilege('buildings_bulk_load.transferred_insert(integer, integer)', 'execute');

ROLLBACK;
