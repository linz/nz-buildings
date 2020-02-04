-- Verify nz-buildings:buildings_reference/functions/update_suburb_locality_changed_deleted_buildings on pg

BEGIN;

DO $$
BEGIN
    PERFORM *
    FROM pg_proc
    WHERE proname = 'suburb_locality_insert_new_areas';
    IF FOUND THEN
        RAISE EXCEPTION 'Dropped function found.';
    END IF;
END $$;

DO $$
BEGIN
    PERFORM *
    FROM pg_proc
    WHERE proname = 'suburb_locality_update_suburb_locality';
    IF FOUND THEN
        RAISE EXCEPTION 'Dropped function found.';
    END IF;
END $$;

DO $$
BEGIN
    PERFORM *
    FROM pg_proc
    WHERE proname = 'suburb_locality_delete_removed_areas';
    IF FOUND THEN
        RAISE EXCEPTION 'Dropped function found.';
    END IF;
END $$;

DO $$
BEGIN
    PERFORM *
    FROM pg_proc
    WHERE proname = 'building_outlines_update_suburb';
    IF FOUND THEN
        RAISE EXCEPTION 'Dropped function found.';
    END IF;
END $$;

DO $$
BEGIN
    PERFORM *
    FROM pg_proc
    WHERE proname = 'bulk_load_outlines_update_all_suburbs';
    IF FOUND THEN
        RAISE EXCEPTION 'Dropped function found.';
    END IF;
END $$;

SELECT has_function_privilege('buildings_reference.building_outlines_update_changed_and_deleted_suburb()', 'execute');

SELECT has_function_privilege('buildings_reference.building_outlines_update_added_suburb()', 'execute');

ROLLBACK;
