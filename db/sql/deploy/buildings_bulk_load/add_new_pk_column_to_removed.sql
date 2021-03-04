-- Deploy nz-buildings:buildings_bulk_load/add_new_pk_column_to_removed to pg

BEGIN;

ALTER TABLE buildings_bulk_load.removed DROP CONSTRAINT removed_pkey;

ALTER TABLE buildings_bulk_load.removed ADD COLUMN supplied_dataset_id integer;
ALTER TABLE buildings_bulk_load.removed ADD CONSTRAINT removed_supplied_dataset_id_fkey
  FOREIGN KEY (supplied_dataset_id) REFERENCES buildings_bulk_load.supplied_datasets(supplied_dataset_id);

UPDATE buildings_bulk_load.removed r
SET supplied_dataset_id = ese.supplied_dataset_id
FROM buildings_bulk_load.existing_subset_extracts ese
WHERE r.building_outline_id = ese.building_outline_id;

ALTER TABLE buildings_bulk_load.removed ALTER COLUMN supplied_dataset_id SET NOT NULL;

ALTER TABLE buildings_bulk_load.removed ADD COLUMN removed_id serial PRIMARY KEY;

COMMIT;
