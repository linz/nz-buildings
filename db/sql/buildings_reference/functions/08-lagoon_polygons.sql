--------------------------------------------
-- buildings_reference.lagoon_polygons

-- Functions

-- lagoon_polygons_delete_by_external_id
    -- params: integer external_lagoon_polygon_id
    -- return: integer lagoon_polygon_id

-- lagoon_polygons_insert
    -- params: integer external_lagoon_polygon_id, varchar geometry
    -- return: integer lagoon_polygon_id


--------------------------------------------

-- Functions

-- lagoon_polygons_delete_by_external_id ()
    -- params: integer external_lagoon_polygon_id
    -- return: integer lagoon_polygon_id

CREATE OR REPLACE FUNCTION buildings_reference.lagoon_polygons_delete_by_external_id(integer)
RETURNS integer AS
$$
    DELETE FROM buildings_reference.lagoon_polygons
    WHERE external_lagoon_polygon_id = $1
    RETURNING lagoon_polygon_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.lagoon_polygons_delete_by_external_id(integer) IS
'Delete from lagoon polygons table by external id';


-- lagoon_polygons_insert
    -- params: integer external_lagoon_polygon_id, varchar geometry
    -- return: integer lagoon_polygon_id

CREATE OR REPLACE FUNCTION buildings_reference.lagoon_polygons_insert(integer, varchar)
RETURNS integer AS
$$
    INSERT INTO buildings_reference.lagoon_polygons (external_lagoon_polygon_id, shape)
    VALUES ($1, ST_SetSRID(ST_GeometryFromText($2), 2193))
    RETURNING lagoon_polygon_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.lagoon_polygons_insert(integer, varchar) IS
'Insert new entry into lagoon polygons table';


-- lagoon_polygons_update_shape_by_external_id
    -- params: integer external_lagoon_polygon_id, varchar geometry
    -- return: integer lagoon_polygon_id

CREATE OR REPLACE FUNCTION buildings_reference.lagoon_polygons_update_shape_by_external_id(integer, varchar)
RETURNS integer AS
$$
    UPDATE buildings_reference.lagoon_polygons
    SET shape = ST_SetSRID(ST_GeometryFromText($2), 2193)
    WHERE external_lagoon_polygon_id = $1
    RETURNING lagoon_polygon_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.lagoon_polygons_update_shape_by_external_id(integer, varchar) IS
'Update geometry of lagoon based on external_river_polygon_id';
