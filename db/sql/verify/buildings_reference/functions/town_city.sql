-- Verify nz-buildings:buildings_reference/functions/town_city on pg

BEGIN;

SELECT has_function_privilege('buildings_reference.town_city_intersect_polygon(geometry)', 'execute');
DO $$
BEGIN

    PERFORM proname, proargnames, prosrc 
    FROM pg_proc
    WHERE proname = 'town_city_intersect_polygon'
    AND prosrc LIKE '%WITH intersecting_town_citys AS%';

    IF NOT FOUND THEN
        RAISE EXCEPTION '"WITH intersecting_town_citys AS" not found';
    END IF;

END $$;

SELECT has_function_privilege('buildings_reference.town_city_delete_removed_areas()', 'execute');

SELECT has_function_privilege('buildings_reference.town_city_insert_new_areas()', 'execute');

SELECT has_function_privilege('buildings_reference.town_city_update_areas()', 'execute');

ROLLBACK;
