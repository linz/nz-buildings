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
    AND prosrc LIKE '%suburb_locality.suburb_locality%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'suburb_locality column not found.';
    END IF;

END $$;

DO $$
BEGIN
    PERFORM proname, proargnames, prosrc 
    FROM pg_proc
    WHERE proname = 'nz_building_outlines_all_sources_insert'
    AND prosrc LIKE '%suburb_locality.suburb_locality%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'suburb_locality column not found.';
    END IF;
END $$;

DO $$
BEGIN

    PERFORM proname, proargnames, prosrc 
    FROM pg_proc
    WHERE proname = 'nz_building_outlines_insert'
    AND prosrc LIKE '%suburb_3rd%';
    IF FOUND THEN
        RAISE EXCEPTION 'suburb_3rd found, should have been replaced by one name column.';
    END IF;

END $$;

DO $$
BEGIN
    PERFORM proname, proargnames, prosrc 
    FROM pg_proc
    WHERE proname = 'nz_building_outlines_all_sources_insert'
    AND prosrc LIKE '%suburb_3rd%';
    IF FOUND THEN
        RAISE EXCEPTION 'suburb_3rd found, should have been replaced by one name column.';
    END IF;
END $$;

ROLLBACK;
