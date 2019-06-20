-- Deploy nz-buildings:buildings_reference/functions/shelter_points to pg

BEGIN;

--------------------------------------------
-- buildings_reference.shelter_points

-- Functions

-- shelter_points_delete_by_external_id
    -- params: integer external_shelter_points_id
    -- return: integer shelter_points_id

-- shelter_points_insert
    -- params: integer external_shelter_points_id, varchar geometry
    -- return: integer shelter_points_id


--------------------------------------------

-- Functions

-- shelter_points_delete_by_external_id ()
    -- params: integer external_shelter_points_id
    -- return: integer shelter_points_id

CREATE OR REPLACE FUNCTION buildings_reference.shelter_points_delete_by_external_id(integer)
RETURNS integer AS
$$

    DELETE FROM buildings_reference.shelter_points
    WHERE external_shelter_points_id = $1
    RETURNING shelter_points_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.shelter_points_delete_by_external_id(integer) IS
'Delete from shelter_points table by external id';


-- shelter_points_insert
    -- params: integer external_shelter_points_id, varchar geometry
    -- return: integer shelter_points_id

CREATE OR REPLACE FUNCTION buildings_reference.shelter_points_insert(integer, varchar)
RETURNS integer AS
$$

    INSERT INTO buildings_reference.shelter_points (external_shelter_points_id, shape)
    VALUES ($1, ST_SetSRID(ST_GeometryFromText($2), 2193))
    RETURNING shelter_points_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.shelter_points_insert(integer, varchar) IS
'Insert new entry into shelter_points table';


-- shelter_points_update_shape_by_external_id
    -- params: integer external_shelter_points_id, varchar geometry
    -- return: integer shelter_points_id

CREATE OR REPLACE FUNCTION buildings_reference.shelter_points_update_shape_by_external_id(integer, varchar)
RETURNS integer AS
$$

    UPDATE buildings_reference.shelter_points
    SET shape = ST_SetSRID(ST_GeometryFromText($2), 2193)
    WHERE external_shelter_points_id = $1
    RETURNING shelter_points_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.shelter_points_update_shape_by_external_id(integer, varchar) IS
'Update geometry of shelters based on external_shelter_points_id';

COMMIT;