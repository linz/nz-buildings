-- Revert buildings:buildings_reference/functions/town_city from pg

BEGIN;

DROP FUNCTION buildings_reference.town_city_intersect_polygon(geometry);

DROP FUNCTION buildings_reference.bulk_load_outlines_update_town_city(integer);

COMMIT;
