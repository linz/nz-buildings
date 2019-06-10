-- Revert nz-buildings:buildings_bulk_load/functions/matched from pg

BEGIN;

DROP FUNCTION buildings_bulk_load.building_outlines_matched_select_by_dataset(integer);

DROP FUNCTION buildings_bulk_load.matched_delete_existing_outlines(integer);

DROP FUNCTION buildings_bulk_load.matched_find_building_id(integer);

DROP FUNCTION buildings_bulk_load.matched_insert_building_outlines(integer, integer);

DROP FUNCTION buildings_bulk_load.matched_select_by_dataset(integer);

DROP FUNCTION buildings_bulk_load.matched_update_qa_status_id(integer, integer, integer);

COMMIT;
