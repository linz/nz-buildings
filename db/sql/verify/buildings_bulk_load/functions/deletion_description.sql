-- Verify nz-buildings:buildings_bulk_load/functions/deletion_description on pg

BEGIN;

SELECT has_function_privilege('buildings_bulk_load.delete_deleted_description(integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.deletion_description_insert(integer, varchar(250))', 'execute');

ROLLBACK;
