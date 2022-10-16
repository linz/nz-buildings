-- Verify nz-buildings:buildings_reference/functions/territorial_authority on pg

BEGIN;

SELECT has_function_privilege('buildings_reference.territorial_authority_grid_intersect_polygon(geometry)', 'execute');
DO $$
BEGIN

    PERFORM proname, proargnames, prosrc 
    FROM pg_proc
    WHERE proname = 'territorial_authority_grid_intersect_polygon'
    AND prosrc LIKE '%WITH intersecting_territorial_authority_grids AS%';

    IF NOT FOUND THEN
        RAISE EXCEPTION '"WITH intersecting_territorial_authority_grids AS" not found';
    END IF;

END $$;

SELECT has_function_privilege('buildings_reference.territorial_authority_intersect_polygon(geometry)', 'execute');

SELECT has_function_privilege('buildings_reference.territorial_auth_delete_areas()', 'execute');

SELECT has_function_privilege('buildings_reference.territorial_auth_insert_areas()', 'execute');

SELECT has_function_privilege('buildings_reference.territorial_auth_update_areas()', 'execute');

DO $$
BEGIN

    PERFORM proname, proargnames, prosrc 
    FROM pg_proc
    WHERE proname = 'territorial_auth_update_areas'
    AND prosrc LIKE '%JOIN%';
    IF FOUND THEN
        RAISE EXCEPTION 'JOIN found.';
    END IF;

END $$;

ROLLBACK;
