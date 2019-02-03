-- Deploy buildings:buildings/functions/buildings to pg

BEGIN;

--------------------------------------------
-- buildings.buildings

-- Functions:
-- buildings_insert (insert new entry into buildings table)
    -- params: None
    -- return: new building_id

-- buildings_update_end_lifespan (update the end lifespan attr of building to now)
    -- params: integer[], building_ids
    -- return: number of outlines updated

--------------------------------------------

-- Functions

-- buildings_insert (insert new entry into buildings table)
    -- params: None
    -- return: new building_id

CREATE OR REPLACE FUNCTION buildings.buildings_insert()
RETURNS integer AS
$$

    INSERT INTO buildings.buildings(
          building_id
        , begin_lifespan
    )
    VALUES (
          DEFAULT -- sequence
        , DEFAULT -- now()
    )
    RETURNING building_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings.buildings_insert() IS
'Insert new building into buildings table using defaults';


-- buildings_update_end_lifespan (update the end lifespan attr of building to now)
    -- params: integer[], building_ids
    -- return: number of outlines updated

CREATE OR REPLACE FUNCTION buildings.buildings_update_end_lifespan(integer[])
    RETURNS integer AS
$$

    WITH update_buildings AS (
        UPDATE buildings.buildings
        SET end_lifespan = now()
        WHERE building_id = ANY($1)
        RETURNING *
    )
    SELECT count(*)::integer FROM update_buildings;

$$ LANGUAGE sql;

COMMENT ON FUNCTION buildings.buildings_update_end_lifespan(integer[]) IS
'Update end_lifespan in buildings table';

COMMIT;
