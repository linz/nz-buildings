-- Deploy nz-buildings:buildings_reference/functions/pond_polygons to pg

BEGIN;

--------------------------------------------
-- buildings_reference.pond_polygons

-- Functions

-- pond_polygons_delete_by_external_id
    -- params: integer external_pond_polygon_id
    -- return: integer pond_polygon_id

-- pond_polygons_insert
    -- params: integer external_pond_polygon_id, varchar geometry
    -- return: integer pond_polygon_id


--------------------------------------------

-- Functions

-- pond_polygons_delete_by_external_id ()
    -- params: integer external_pond_polygon_id
    -- return: integer pond_polygon_id

CREATE OR REPLACE FUNCTION buildings_reference.pond_polygons_delete_by_external_id(integer)
RETURNS integer AS
$$

    DELETE FROM buildings_reference.pond_polygons
    WHERE external_pond_polygon_id = $1
    RETURNING pond_polygon_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.pond_polygons_delete_by_external_id(integer) IS
'Delete from pond polygons table by external id';


-- pond_polygons_insert
    -- params: integer external_pond_polygon_id, varchar geometry
    -- return: integer pond_polygon_id

CREATE OR REPLACE FUNCTION buildings_reference.pond_polygons_insert(integer, varchar)
RETURNS integer AS
$$

    INSERT INTO buildings_reference.pond_polygons (external_pond_polygon_id, shape)
    VALUES ($1, ST_SetSRID(ST_GeometryFromText($2), 2193))
    RETURNING pond_polygon_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.pond_polygons_insert(integer, varchar) IS
'Insert new entry into pond polygons table';


-- pond_polygons_update_shape_by_external_id
    -- params: integer external_pond_polygon_id, varchar geometry
    -- return: integer pond_polygon_id

CREATE OR REPLACE FUNCTION buildings_reference.pond_polygons_update_shape_by_external_id(integer, varchar)
RETURNS integer AS
$$

    UPDATE buildings_reference.pond_polygons
    SET shape = ST_SetSRID(ST_GeometryFromText($2), 2193)
    WHERE external_pond_polygon_id = $1
    RETURNING pond_polygon_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.pond_polygons_update_shape_by_external_id(integer, varchar) IS
'Update geometry of pond based on external_river_polygon_id';

COMMIT;
