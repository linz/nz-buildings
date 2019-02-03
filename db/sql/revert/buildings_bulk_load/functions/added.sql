-- Revert buildings:buildings_bulk_load/functions/added from pg

BEGIN;

DROP FUNCTION buildings_bulk_load.added_delete_bulk_load_outlines(integer);

DROP FUNCTION buildings_bulk_load.added_insert_all_bulk_loaded_outlines(integer);

DROP FUNCTION buildings_bulk_load.added_insert_bulk_load_outlines(integer, integer);

DROP FUNCTION buildings_bulk_load.added_select_by_dataset(integer);

COMMIT;
