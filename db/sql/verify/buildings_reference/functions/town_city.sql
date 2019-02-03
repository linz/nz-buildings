-- Verify buildings:buildings_reference/functions/town_city on pg

BEGIN;

SELECT has_function_privilege('buildings_reference.town_city_intersect_polygon(geometry)', 'execute');

SELECT has_function_privilege('buildings_reference.bulk_load_outlines_update_town_city(integer)', 'execute');

ROLLBACK;
