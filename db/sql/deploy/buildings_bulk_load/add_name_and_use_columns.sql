-- Deploy nz-buildings:buildings_bulk_load/add_name_and_use_columns to pg

BEGIN;

ALTER TABLE buildings_bulk_load.bulk_load_outlines
ADD COLUMN bulk_load_use_id integer,
ADD COLUMN bulk_load_name varchar(250);

COMMIT;
