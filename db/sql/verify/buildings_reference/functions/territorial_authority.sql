-- Verify nz-buildings:buildings_reference/functions/territorial_authority on pg

BEGIN;

SELECT has_function_privilege('buildings_reference.territorial_authority_grid_intersect_polygon(geometry)', 'execute');

SELECT has_function_privilege('buildings_reference.territorial_authority_intersect_polygon(geometry)', 'execute');

SELECT has_function_privilege('buildings_reference.territorial_authority_delete_by_external_id(integer)', 'execute');

SELECT has_function_privilege('buildings_reference.territorial_authority_insert(integer, varchar, varchar)', 'execute');

SELECT has_function_privilege('buildings_reference.territorial_authority_update_by_external_id(integer, varchar, varchar)', 'execute');

SELECT has_function_privilege('buildings_reference.territorial_authority_attribute_update_building_outlines(integer[])', 'execute');

SELECT has_function_privilege('buildings_reference.territorial_authority_geometry_update_building_outlines(varchar)', 'execute');

DO $$
BEGIN
    PERFORM *
    FROM pg_proc
    WHERE proname = 'territorial_auth_delete_areas'
    AND pronargs = 0;
    IF FOUND THEN
        RAISE EXCEPTION 'Dropped function found.';
    END IF;
END $$;

DO $$
BEGIN
    PERFORM *
    FROM pg_proc
    WHERE proname = 'territorial_auth_insert_areas'
    AND pronargs = 0;
    IF FOUND THEN
        RAISE EXCEPTION 'Dropped function found.';
    END IF;
END $$;

DO $$
BEGIN
    PERFORM *
    FROM pg_proc
    WHERE proname = 'territorial_auth_update_areas'
    AND pronargs = 0;
    IF FOUND THEN
        RAISE EXCEPTION 'Dropped function found.';
    END IF;
END $$;

ROLLBACK;
