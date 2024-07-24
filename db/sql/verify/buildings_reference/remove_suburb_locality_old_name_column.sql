-- Verify nz-buildings:buildings_reference/remove_suburb_locality_old_name_column on pg

BEGIN;

DO $$
BEGIN

    PERFORM column_name
    FROM information_schema.columns
    WHERE table_schema = 'buildings_reference'
	AND table_name = 'suburb_locality'
	AND column_name in ('suburb_4th', 'suburb_3rd', 'suburb_2nd', 'suburb_1st');

    IF FOUND THEN
        RAISE EXCEPTION 'Columns suburb_4th, suburb_3rd, suburb_2nd, suburb_1st Found.';
    END IF;

END $$;

ROLLBACK;
