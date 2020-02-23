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
    AND prosrc LIKE '%nz_imagery_survey_index%';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'nz_imagery_survey_index not found.';
    END IF;

END $$;

DO $$
BEGIN

    PERFORM proname, proargnames, prosrc 
    FROM pg_proc
    WHERE proname = 'nz_building_outlines_all_sources_insert'
    AND prosrc LIKE '%nz_imagery_survey_index%';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'nz_imagery_survey_index not found.';
    END IF;

END $$;

ROLLBACK;
