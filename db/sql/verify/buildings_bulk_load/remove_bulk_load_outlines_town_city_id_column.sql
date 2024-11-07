-- Verify nz-buildings:buildings_bulk_load/remove_bulk_load_outlines_town_city_id_column on pg

BEGIN;

DO $$
BEGIN

    PERFORM column_name
    FROM information_schema.columns
    WHERE table_schema = 'buildings_bulk_load'
	AND table_name = 'bulk_load_outlines'
	AND column_name = 'town_city';

    IF FOUND THEN
        RAISE EXCEPTION 'Dropped column town_city Found.';
    END IF;

END $$;

ROLLBACK;
