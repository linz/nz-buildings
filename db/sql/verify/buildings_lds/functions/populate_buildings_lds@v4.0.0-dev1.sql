-- Verify nz-buildings:buildings_lds/functions/populate_buildings_lds on pg

BEGIN;

SELECT has_function_privilege('buildings_lds.nz_building_outlines_insert()', 'execute');

SELECT has_function_privilege('buildings_lds.nz_building_outlines_all_sources_insert()', 'execute');

SELECT has_function_privilege('buildings_lds.nz_building_outlines_lifecycle_insert()', 'execute');

SELECT has_function_privilege('buildings_lds.populate_buildings_lds()', 'execute');

DO $$
BEGIN

    PERFORM proname, proargnames, prosrc 
    FROM pg_proc
    WHERE proname = 'nz_building_outlines_insert'
    AND prosrc LIKE '%suburb_3rd%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'suburb_3rd not found.';
    END IF;

END $$;

DO $$
BEGIN
    PERFORM proname, proargnames, prosrc 
    FROM pg_proc
    WHERE proname = 'nz_building_outlines_all_sources_insert'
    AND prosrc LIKE '%suburb_3rd%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'suburb_3rd not found.';
    END IF;
END $$;

DO $$
BEGIN
    PERFORM proname, proargnames, prosrc 
    FROM pg_proc
    WHERE proname = 'nz_building_outlines_all_sources_insert'
    AND prosrc LIKE '%deleted_in_production.building_outline_id IS NULL%';
    IF FOUND THEN
        RAISE EXCEPTION 'Building outlines that are deleted in production should not be excluded.';
    END IF;
END $$;

DO $$
BEGIN
    PERFORM proname, proargnames, prosrc 
    FROM pg_proc
    WHERE proname = 'nz_building_outlines_insert'
    AND prosrc LIKE '%aerial_lds.nz_imagery_survey_index%';
    IF FOUND THEN
        RAISE EXCEPTION 'aerial_lds found - should now refer to buildings_reference';
    END IF;
END $$;

DO $$
BEGIN
    PERFORM proname, proargnames, prosrc 
    FROM pg_proc
    WHERE proname = 'nz_building_outlines_all_sources_insert'
    AND prosrc LIKE '%aerial_lds.nz_imagery_survey_index%';
    IF FOUND THEN
        RAISE EXCEPTION 'aerial_lds found - should now refer to buildings_reference';
    END IF;
END $$;

DO $$
BEGIN
    PERFORM proname, proargnames, prosrc 
    FROM pg_proc
    WHERE proname = 'nz_building_outlines_insert'
    AND prosrc LIKE '%building_name.begin_lifespan%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'building_name date not taken into account for published last_modified date';
    END IF;
END $$;

DO $$
BEGIN
    PERFORM proname, proargnames, prosrc 
    FROM pg_proc
    WHERE proname = 'nz_building_outlines_all_sources_insert'
    AND prosrc LIKE '%building_name.begin_lifespan%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'building_name date not taken into account for published last_modified date';
    END IF;
END $$;

ROLLBACK;
