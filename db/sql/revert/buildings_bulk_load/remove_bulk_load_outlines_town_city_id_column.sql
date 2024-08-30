-- Revert nz-buildings:buildings_bulk_load/remove_bulk_load_outlines_town_city_id_column from pg

BEGIN;

ALTER TABLE buildings_bulk_load.bulk_load_outlines
ADD COLUMN town_city_id integer;

COMMIT;
