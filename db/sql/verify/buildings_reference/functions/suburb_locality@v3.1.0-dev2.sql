-- Verify nz-buildings:buildings_reference/functions/suburb_locality on pg

BEGIN;

SELECT has_function_privilege('buildings_reference.suburb_locality_intersect_polygon(geometry)', 'execute');

SELECT has_function_privilege('buildings_reference.suburb_locality_delete_removed_areas()', 'execute');

SELECT has_function_privilege('buildings_reference.suburb_locality_insert_new_areas()', 'execute');

SELECT has_function_privilege('buildings_reference.suburb_locality_update_suburb_locality()', 'execute');

DO $$
BEGIN

    PERFORM proname, proargnames, prosrc 
    FROM pg_proc
    WHERE proname = 'suburb_locality_insert_new_areas'
    AND prosrc LIKE '%PARK_RESERVE%';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'PARK_RESERVE not found.';
    END IF;

END $$;

ROLLBACK;
