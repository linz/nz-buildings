-- Deploy buildings:buildings_bulk_load/functions/transferred to pg

BEGIN;

--------------------------------------------
-- buildings_bulk_load.transferred

-- Functions:

-- transferred_insert (Create new records in transferred table)
	-- params: integer bulk_load_outline_id, integer new_building_outline_id
	-- return: integer count of new outlines in transferred

--------------------------------------------

-- Functions

-- transferred_insert (Create new records in transferred table)
    -- params: integer bulk_load_outline_id, integer new_building_outline_id
    -- return: integer count of new outlines in transferred

CREATE OR REPLACE FUNCTION buildings_bulk_load.transferred_insert(integer, integer)
    RETURNS integer AS
$$

    WITH transferred_insert AS (
        INSERT INTO buildings_bulk_load.transferred(bulk_load_outline_id, new_building_outline_id)
        VALUES($1, $2)
        RETURNING 1
    )
    SELECT count(*)::integer FROM transferred_insert;

$$ LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_bulk_load.transferred_insert(integer, integer) IS
'Create new records in transferred table';


COMMIT;
