--------------------------------------------
-- buildings_reference.swamp_polygons

-- Functions

-- swamp_polygons_delete_by_external_id
    -- params: integer external_swamp_polygon_id
    -- return: integer swamp_polygon_id

-- swamp_polygons_insert
    -- params: integer external_swamp_polygon_id, varchar geometry
    -- return: integer swamp_polygon_id


--------------------------------------------

-- Functions

-- swamp_polygons_delete_by_external_id ()
    -- params: integer external_swamp_polygon_id
    -- return: integer swamp_polygon_id

CREATE OR REPLACE FUNCTION buildings_reference.swamp_polygons_delete_by_external_id(integer)
RETURNS integer AS
$$
    DELETE FROM buildings_reference.swamp_polygons
    WHERE external_swamp_polygon_id = $1
    RETURNING swamp_polygon_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.swamp_polygons_delete_by_external_id(integer) IS
'Delete from swamp polygons table by external id';


-- swamp_polygons_insert
    -- params: integer external_swamp_polygon_id, varchar geometry
    -- return: integer swamp_polygon_id

CREATE OR REPLACE FUNCTION buildings_reference.swamp_polygons_insert(integer, varchar)
RETURNS integer AS
$$
    INSERT INTO buildings_reference.swamp_polygons (external_swamp_polygon_id, shape)
    VALUES ($1, ST_SetSRID(ST_GeometryFromText($2), 2193))
    RETURNING swamp_polygon_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.swamp_polygons_insert(integer, varchar) IS
'Insert new entry into swamp polygons table';


-- swamp_polygons_update_shape_by_external_id
    -- params: integer external_swamp_polygon_id, varchar geometry
    -- return: integer swamp_polygon_id

CREATE OR REPLACE FUNCTION buildings_reference.swamp_polygons_update_shape_by_external_id(integer, varchar)
RETURNS integer AS
$$
    UPDATE buildings_reference.swamp_polygons
    SET shape = ST_SetSRID(ST_GeometryFromText($2), 2193)
    WHERE external_swamp_polygon_id = $1
    RETURNING swamp_polygon_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.swamp_polygons_update_shape_by_external_id(integer, varchar) IS
'Update geometry of swamp based on external_river_polygon_id';
