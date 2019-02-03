-- Verify buildings:buildings_common/functions/capture_method on pg

BEGIN;

SELECT has_function_privilege('buildings_common.capture_method_insert(varchar(250))', 'execute');

ROLLBACK;
