-- Deploy nz-buildings:buildings_reference/functions/bivouac_points to pg

BEGIN;

--------------------------------------------
-- buildings_reference.bivouac_points

-- Functions

-- bivouac_points_delete_by_external_id
    -- params: integer external_bivouac_points_id
    -- return: integer bivouac_points_id

-- bivouac_points_insert
    -- params: integer external_bivouac_points_id, varchar geometry
    -- return: integer bivouac_points_id


--------------------------------------------

-- Functions

-- bivouac_points_delete_by_external_id ()
    -- params: integer external_bivouac_points_id
    -- return: integer bivouac_points_id

CREATE OR REPLACE FUNCTION buildings_reference.bivouac_points_delete_by_external_id(integer)
RETURNS integer AS
$$

    DELETE FROM buildings_reference.bivouac_points
    WHERE external_bivouac_points_id = $1
    RETURNING bivouac_points_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.bivouac_points_delete_by_external_id(integer) IS
'Delete from bivouac_points table by external id';


-- bivouac_points_insert
    -- params: integer external_bivouac_points_id, varchar geometry
    -- return: integer bivouac_points_id

CREATE OR REPLACE FUNCTION buildings_reference.bivouac_points_insert(integer, varchar)
RETURNS integer AS
$$

    INSERT INTO buildings_reference.bivouac_points (external_bivouac_points_id, shape)
    VALUES ($1, ST_SetSRID(ST_GeometryFromText($2), 2193))
    RETURNING bivouac_points_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.bivouac_points_insert(integer, varchar) IS
'Insert new entry into bivouac_points table';


-- bivouac_points_update_shape_by_external_id
    -- params: integer external_bivouac_points_id, varchar geometry
    -- return: integer bivouac_points_id

CREATE OR REPLACE FUNCTION buildings_reference.bivouac_points_update_shape_by_external_id(integer, varchar)
RETURNS integer AS
$$

    UPDATE buildings_reference.bivouac_points
    SET shape = ST_SetSRID(ST_GeometryFromText($2), 2193)
    WHERE external_bivouac_points_id = $1
    RETURNING bivouac_points_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.bivouac_points_update_shape_by_external_id(integer, varchar) IS
'Update geometry of bivouacs based on external_bivouac_points_id';

COMMIT;