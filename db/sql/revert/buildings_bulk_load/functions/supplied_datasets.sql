-- Revert nz-buildings:buildings_bulk_load/functions/supplied_datasets from pg

BEGIN;

DROP FUNCTION buildings_bulk_load.supplied_datasets_insert(varchar(250), integer);

DROP FUNCTION buildings_bulk_load.supplied_datasets_select_transfer_date(integer);

DROP FUNCTION buildings_bulk_load.supplied_datasets_update_processed_date(integer);

DROP FUNCTION buildings_bulk_load.supplied_datasets_update_transfer_date(integer);

COMMIT;
