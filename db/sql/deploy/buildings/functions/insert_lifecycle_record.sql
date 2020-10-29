-- Deploy nz-buildings:buildings/functions/insert_lifecycle_record to pg

BEGIN;

--------------------------------------------
-- buildings.lifecycle

-- Functions:
-- lifecycle_insert_record (add a single new record to lifecycle table)
    -- params: integer, integer
    -- return: building_id

--------------------------------------------

-- Functions

-- lifecycle_insert_record (add new record to lifecycle table)
    -- params: integer, integer
    -- return: building_id

CREATE OR REPLACE FUNCTION buildings.lifecycle_insert_record(integer, integer)
RETURNS integer AS
$$

    INSERT INTO buildings.lifecycle(
          parent_building_id
        , building_id
    )
    VALUES(
        $1, 
        $2
    )
    RETURNING building_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings.lifecycle_insert_record(integer, integer) IS
'Inserts a single new records in lifecycle table';

COMMIT;
