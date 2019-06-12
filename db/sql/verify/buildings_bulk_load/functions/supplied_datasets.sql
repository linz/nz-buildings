-- Verify nz-buildings:buildings_bulk_load/functions/supplied_datasets on pg

BEGIN;

SELECT has_function_privilege('buildings_bulk_load.supplied_datasets_insert(varchar(250), integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.supplied_datasets_select_transfer_date(integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.supplied_datasets_update_processed_date(integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.supplied_datasets_update_transfer_date(integer)', 'execute');

ROLLBACK;
