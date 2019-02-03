-- Deploy buildings:buildings_reference/functions/lake_polygons to pg

BEGIN;

--------------------------------------------
-- buildings_reference.lake_polygons

-- Functions

-- lake_polygons_delete_by_external_id
    -- params: integer external_lake_polygon_id
    -- return: integer lake_polygon_id

-- lake_polygons_insert
    -- params: integer external_lake_polygon_id, varchar geometry
    -- return: integer lake_polygon_id


--------------------------------------------

-- Functions

-- lake_polygons_delete_by_external_id ()
    -- params: integer external_lake_polygon_id
    -- return: integer lake_polygon_id

CREATE OR REPLACE FUNCTION buildings_reference.lake_polygons_delete_by_external_id(integer)
RETURNS integer AS
$$
    DELETE FROM buildings_reference.lake_polygons
    WHERE external_lake_polygon_id = $1
    RETURNING lake_polygon_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.lake_polygons_delete_by_external_id(integer) IS
'Delete from lake polygons table by external id';


-- lake_polygons_insert
    -- params: integer external_lake_polygon_id, varchar geometry
    -- return: integer lake_polygon_id

CREATE OR REPLACE FUNCTION buildings_reference.lake_polygons_insert(integer, varchar)
RETURNS integer AS
$$
    INSERT INTO buildings_reference.lake_polygons (external_lake_polygon_id, shape)
    VALUES ($1, ST_SetSRID(ST_GeometryFromText($2), 2193))
    RETURNING lake_polygon_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.lake_polygons_insert(integer, varchar) IS
'Insert new entry into lake polygons table';


-- lake_polygons_update_shape_by_external_id
    -- params: integer external_lake_polygon_id, varchar geometry
    -- return: integer lake_polygon_id

CREATE OR REPLACE FUNCTION buildings_reference.lake_polygons_update_shape_by_external_id(integer, varchar)
RETURNS integer AS
$$
    UPDATE buildings_reference.lake_polygons
    SET shape = ST_SetSRID(ST_GeometryFromText($2), 2193)
    WHERE external_lake_polygon_id = $1
    RETURNING lake_polygon_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.lake_polygons_update_shape_by_external_id(integer, varchar) IS
'Update geometry of lake based on external_river_polygon_id';

COMMIT;
