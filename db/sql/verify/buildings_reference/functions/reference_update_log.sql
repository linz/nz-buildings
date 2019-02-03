-- Verify buildings:buildings_reference/functions/reference_update_log on pg

BEGIN;

SELECT has_function_privilege('buildings_reference.reference_update_log_insert_log(varchar[])', 'execute');

ROLLBACK;
