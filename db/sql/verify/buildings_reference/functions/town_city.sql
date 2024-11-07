-- Verify nz-buildings:buildings_reference/functions/town_city on pg

BEGIN;

DO $$
BEGIN
    PERFORM *
    FROM pg_proc
    WHERE proname = 'town_city_intersect_polygon'
    AND pronargs = 1;
    IF FOUND THEN
        RAISE EXCEPTION 'Dropped function found.';
    END IF;
END $$;

DO $$
BEGIN
    PERFORM *
    FROM pg_proc
    WHERE proname = 'town_city_delete_removed_areas'
    AND pronargs = 0;
    IF FOUND THEN
        RAISE EXCEPTION 'Dropped function found.';
    END IF;
END $$;

DO $$
BEGIN
    PERFORM *
    FROM pg_proc
    WHERE proname = 'town_city_insert_new_areas'
    AND pronargs = 0;
    IF FOUND THEN
        RAISE EXCEPTION 'Dropped function found.';
    END IF;
END $$;

DO $$
BEGIN
    PERFORM *
    FROM pg_proc
    WHERE proname = 'town_city_update_areas'
    AND pronargs = 0;
    IF FOUND THEN
        RAISE EXCEPTION 'Dropped function found.';
    END IF;
END $$;

ROLLBACK;
