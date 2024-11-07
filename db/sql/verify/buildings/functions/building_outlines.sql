-- Verify nz-buildings:buildings/functions/building_outlines on pg

BEGIN;

DO $$
BEGIN
    PERFORM *
    FROM pg_proc
    WHERE proname = 'building_outlines_update_suburb';
    IF FOUND THEN
        RAISE EXCEPTION 'Dropped function found.';
    END IF;
END $$;

SELECT has_function_privilege('buildings.building_outlines_insert(integer, integer, integer, integer, integer, integer, geometry)', 'execute');

SELECT has_function_privilege('buildings.building_outlines_insert_bulk(integer, integer)', 'execute');

SELECT has_function_privilege('buildings.building_outlines_update_attributes(integer, integer, integer, integer, integer, integer)', 'execute');

SELECT has_function_privilege('buildings.building_outlines_update_capture_method(integer, integer)', 'execute');

SELECT has_function_privilege('buildings.building_outlines_update_end_lifespan(integer[])', 'execute');

SELECT has_function_privilege('buildings.building_outlines_update_shape(geometry, integer)', 'execute');

SELECT has_function_privilege('buildings.building_outlines_update_territorial_authority(integer[])', 'execute');

SELECT has_function_privilege('buildings.building_outlines_update_modified_date(integer)', 'execute');

SELECT has_function_privilege('buildings.building_outlines_update_modified_date_by_building_id(integer)', 'execute');

DO $$
BEGIN
    PERFORM *
    FROM pg_proc
    WHERE proname = 'building_outlines_insert'
    AND pronargs = 8;
    IF FOUND THEN
        RAISE EXCEPTION 'Dropped function found.';
    END IF;
END $$;

DO $$
BEGIN
    PERFORM *
    FROM pg_proc
    WHERE proname = 'building_outlines_update_attributes'
    AND pronargs = 7;
    IF FOUND THEN
        RAISE EXCEPTION 'Dropped function found.';
    END IF;
END $$;

DO $$
BEGIN
    PERFORM *
    FROM pg_proc
    WHERE proname = 'building_outlines_update_town_city'
    AND pronargs = 1;
    IF FOUND THEN
        RAISE EXCEPTION 'Dropped function found.';
    END IF;
END $$;

ROLLBACK;
