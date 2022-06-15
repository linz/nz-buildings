-- Verify nz-buildings:buildings_bulk_load/functions/load_to_production on pg

BEGIN;

DO $$
BEGIN

    PERFORM proname, proargnames, prosrc
    FROM pg_proc
    WHERE proname = 'load_to_production'
    AND prosrc LIKE '%building_name_removed_insert_bulk%';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'building_name_removed_insert_bulk not found.';
    END IF;

END $$;

ROLLBACK;
