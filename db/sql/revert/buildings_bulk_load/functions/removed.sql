-- Revert buildings:buildings_bulk_load/functions/removed from pg

BEGIN;

DROP FUNCTION buildings_bulk_load.building_outlines_removed_select_by_dataset(integer);

DROP FUNCTION buildings_bulk_load.buildings_removed_select_by_dataset(integer);

DROP FUNCTION buildings_bulk_load.removed_delete_existing_outline(integer);

DROP FUNCTION buildings_bulk_load.removed_delete_existing_outlines(integer[]);

DROP FUNCTION buildings_bulk_load.removed_insert_building_outlines(integer);

DROP FUNCTION buildings_bulk_load.removed_update_qa_status_id(integer, integer);

COMMIT;
