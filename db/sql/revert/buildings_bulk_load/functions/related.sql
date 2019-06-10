-- Revert nz-buildings:buildings_bulk_load/functions/related from pg

BEGIN;

DROP FUNCTION buildings_bulk_load.building_outlines_related_select_by_dataset(integer);

DROP FUNCTION buildings_bulk_load.buildings_related_select_by_dataset(integer);

DROP FUNCTION buildings_bulk_load.related_delete_existing_outlines(integer);

DROP FUNCTION buildings_bulk_load.related_insert_building_outlines(integer, integer, integer);

DROP FUNCTION buildings_bulk_load.related_group_insert();

DROP FUNCTION buildings_bulk_load.related_select_by_dataset(integer);

DROP FUNCTION buildings_bulk_load.related_update_qa_status_id(integer, integer, integer);

COMMIT;
