-- Deploy buildings:buildings/functions/lifecycle to pg

BEGIN;

--------------------------------------------
-- buildings.lifecycle

-- Functions:
-- lifecycle_add_record (add new record to lifecycle table)
    -- params: integer, integer
    -- return: building_id
--------------------------------------------

-- Functions

-- lifecycle_add_record (add new record to lifecycle table)
    -- params: integer, integer
    -- return: building_id

CREATE OR REPLACE FUNCTION buildings.lifecycle_add_record(integer, integer)
    RETURNS integer AS
$$
    INSERT INTO buildings.lifecycle(
          parent_building_id
        , building_id
    )
    SELECT
          outlines.building_id
        , $1
    FROM buildings_bulk_load.related
    JOIN buildings.building_outlines outlines USING (building_outline_id)
    WHERE related.bulk_load_outline_id = $2
    RETURNING building_id;

$$ LANGUAGE sql;

COMMENT ON FUNCTION buildings.lifecycle_add_record(integer, integer) IS
'Create new records in lifecycle table';

COMMIT;
