-- Verify nz-buildings:buildings_reference/functions/update_suburb_locality_changed_deleted_buildings on pg

BEGIN;

DO $$
BEGIN
    PERFORM *
    FROM pg_proc
    WHERE proname = 'building_outlines_update_changed_and_deleted_suburb'
    AND pronargs = 0;
    IF FOUND THEN
        RAISE EXCEPTION 'Dropped function found.';
    END IF;
END $$;

DO $$
BEGIN
    PERFORM *
    FROM pg_proc
    WHERE proname = 'building_outlines_update_added_suburb'
    AND pronargs = 0;
    IF FOUND THEN
        RAISE EXCEPTION 'Dropped function found.';
    END IF;
END $$;

ROLLBACK;
