-- Verify nz-buildings:buildings_bulk_load/add_new_pk_column_to_removed on pg

BEGIN;

SELECT
      building_outline_id
    , qa_status_id
    , supplied_dataset_id
    , removed_id
FROM buildings_bulk_load.removed
WHERE FALSE;

ROLLBACK;
