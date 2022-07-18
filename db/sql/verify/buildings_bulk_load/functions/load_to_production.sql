-- Verify nz-buildings:buildings_bulk_load/functions/load_to_production on pg

BEGIN;

DO $$
BEGIN

    PERFORM proname, proargnames, prosrc
    FROM pg_proc
    WHERE proname = 'load_building_outlines'
    AND prosrc LIKE '%buildings.building_name_added_insert_bulk%';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'The load_to_production function does not include modifications to handle names and uses.';
    END IF;

END $$;

ROLLBACK;
