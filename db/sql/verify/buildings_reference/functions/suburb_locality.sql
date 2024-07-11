-- Verify nz-buildings:buildings_reference/functions/suburb_locality on pg

BEGIN;

SELECT has_function_privilege('buildings_reference.suburb_locality_intersect_polygon(geometry)', 'execute');

DO $$
BEGIN

    PERFORM proname, proargnames, prosrc 
    FROM pg_proc
    WHERE proname = 'suburb_locality_intersect_polygon'
    AND prosrc LIKE '%WITH intersecting_suburbs AS%';

    IF NOT FOUND THEN
        RAISE EXCEPTION '"WITH intersecting_suburbs AS" not found';
    END IF;

END $$;

ROLLBACK;
