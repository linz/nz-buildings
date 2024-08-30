-- Deploy nz-buildings:buildings_bulk_load/remove_bulk_load_outlines_town_city_id_column to pg

BEGIN;

ALTER TABLE buildings_bulk_load.bulk_load_outlines
DROP COLUMN town_city_id;

COMMIT;
