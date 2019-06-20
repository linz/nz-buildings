-- Deploy nz-buildings:buildings_reference/functions/hut_points to pg

BEGIN;

--------------------------------------------
-- buildings_reference.hut_points

-- Functions

-- hut_points_delete_by_external_id
    -- params: integer external_hut_points_id
    -- return: integer hut_points_id

-- hut_points_insert
    -- params: integer external_hut_points_id, varchar geometry
    -- return: integer hut_points_id


--------------------------------------------

-- Functions

-- hut_points_delete_by_external_id ()
    -- params: integer external_hut_points_id
    -- return: integer hut_points_id

CREATE OR REPLACE FUNCTION buildings_reference.hut_points_delete_by_external_id(integer)
RETURNS integer AS
$$

    DELETE FROM buildings_reference.hut_points
    WHERE external_hut_points_id = $1
    RETURNING hut_points_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.hut_points_delete_by_external_id(integer) IS
'Delete from hut_points table by external id';


-- hut_points_insert
    -- params: integer external_hut_points_id, varchar geometry
    -- return: integer hut_points_id

CREATE OR REPLACE FUNCTION buildings_reference.hut_points_insert(integer, varchar)
RETURNS integer AS
$$

    INSERT INTO buildings_reference.hut_points (external_hut_points_id, shape)
    VALUES ($1, ST_SetSRID(ST_GeometryFromText($2), 2193))
    RETURNING hut_points_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.hut_points_insert(integer, varchar) IS
'Insert new entry into hut_points table';


-- hut_points_update_shape_by_external_id
    -- params: integer external_hut_points_id, varchar geometry
    -- return: integer hut_points_id

CREATE OR REPLACE FUNCTION buildings_reference.hut_points_update_shape_by_external_id(integer, varchar)
RETURNS integer AS
$$

    UPDATE buildings_reference.hut_points
    SET shape = ST_SetSRID(ST_GeometryFromText($2), 2193)
    WHERE external_hut_points_id = $1
    RETURNING hut_points_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.hut_points_update_shape_by_external_id(integer, varchar) IS
'Update geometry of huts based on external_hut_points_id';

COMMIT;