-- Verify nz-buildings:buildings_reference/drop_town_city_table on pg

BEGIN;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_tables
    WHERE schemaname = 'buildings_reference'
    AND tablename  = 'town_city';
    IF FOUND THEN
        RAISE EXCEPTION 'Table buildings_reference.town_city exists but should have been removed';
    END IF;
END;
$$;

DO $$
BEGIN
    PERFORM TRUE
    FROM information_schema.columns 
    WHERE table_schema = 'buildings_reference'
    AND table_name='reference_update_log'
    AND column_name='town_city';
    IF FOUND THEN
        RAISE EXCEPTION 'Column town_city in buildings_reference.reference_update_log exists but should have been removed';
    END IF;

END;
$$;


ROLLBACK;
