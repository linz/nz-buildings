-- Revert nz-buildings:buildings_bulk_load/add_new_pk_column_to_removed from pg

BEGIN;

ALTER TABLE buildings_bulk_load.removed DROP COLUMN removed_id;

ALTER TABLE buildings_bulk_load.removed DROP COLUMN supplied_dataset_id;

ALTER TABLE buildings_bulk_load.removed ADD PRIMARY KEY (building_outline_id);

COMMIT;
