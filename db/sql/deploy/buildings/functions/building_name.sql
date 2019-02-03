-- Deploy buildings:buildings/functions/building_name to pg

BEGIN;

--------------------------------------------
-- buildings.building_name
-- Future enhancement
--------------------------------------------

-- Functions

-- building_name_update_end_lifespan (update the end_endlifespan of building in name table)
    -- params: integer[], building_ids
    -- return: number of outlines updated

CREATE OR REPLACE FUNCTION buildings.building_name_update_end_lifespan(integer[])
    RETURNS integer AS
$$

    WITH update_name AS (
        UPDATE buildings.building_name
        SET end_lifespan = now()
        WHERE building_id = ANY($1)
        RETURNING *
    )
    SELECT count(*)::integer FROM update_name;

$$ LANGUAGE sql;

COMMENT ON FUNCTION buildings.building_name_update_end_lifespan(integer[]) IS
'Update end_lifespan in building_name table';

COMMIT;
