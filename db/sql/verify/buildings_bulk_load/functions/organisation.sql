-- Verify nz-buildings:buildings_bulk_load/functions/organisation on pg

BEGIN;

SELECT has_function_privilege('buildings_bulk_load.organisation_insert(varchar(250))', 'execute');

ROLLBACK;
