-- Revert buildings:buildings_bulk_load/functions/existing_subset_extracts from pg

BEGIN;

DROP FUNCTION buildings_bulk_load.existing_subset_extracts_insert(integer, integer, geometry);

DROP FUNCTION buildings_bulk_load.existing_subset_extracts_update_supplied_dataset(integer, integer);

DROP FUNCTION buildings_bulk_load.existing_subset_extracts_remove_by_building_outline_id(integer[]);

COMMIT;
