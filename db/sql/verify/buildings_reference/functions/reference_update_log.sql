-- Verify nz-buildings:buildings_reference/functions/reference_update_log on pg

BEGIN;

SELECT has_function_privilege('buildings_reference.reference_update_log_insert_log(varchar[])', 'execute');

DO $$
BEGIN

    PERFORM proname, proargnames, prosrc 
    FROM pg_proc
    WHERE proname = 'reference_update_log_insert_log'
    AND prosrc LIKE '%town_city%';
    IF FOUND THEN
        RAISE EXCEPTION 'town_city found, should have been removed.';
    END IF;

    PERFORM proname, proargnames, prosrc 
    FROM pg_proc
    WHERE proname = 'reference_update_log_insert_log'
    AND prosrc LIKE '%hut_points%'
    AND prosrc LIKE '%shelter_points%'
    AND prosrc LIKE '%bivouac_points%'
    AND prosrc LIKE '%protected_areas_polygons%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'dataset keywords not found, should have been added.';
    END IF;

END $$;

ROLLBACK;
