-- Verify nz-buildings:buildings/remove_building_outlines_town_city_id_column on pg

BEGIN;

DO $$
BEGIN

    PERFORM column_name
    FROM information_schema.columns
    WHERE table_schema = 'buildings'
	AND table_name = 'building_outlines'
	AND column_name = 'town_city';

    IF FOUND THEN
        RAISE EXCEPTION 'Dropped column town_city Found.';
    END IF;

END $$;

ROLLBACK;
