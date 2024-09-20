-- Deploy nz-buildings:buildings_reference/functions/territorial_authority to pg

BEGIN;

----------------------------------------------------------------------------------------------
-- buildings_reference.territorial_authority && buildings_reference.territorial_authority_grid

-- Functions

-- territorial_authority_grid_intersect_polygon (id of the TA that has the most overlap)
    -- params: p_polygon_geometry, geometry
    -- return: integer territorial_authority_id

-- territorial_authority_intersect_polygon (id of the TA that has the most overlap)
    -- params: p_polygon_geometry geometry
    -- return: integer territorial_authority_id

-- territorial_authority_delete_by_external_id
    -- params: integer external_territorial_authority_id
    -- return: integer territorial_authority_id

-- territorial_authority_insert
    -- params: integer external_territorial_authority_id, varchar territorial_authority, varchar geometry
    -- return: integer territorial_authority_id

-- territorial_authority_update_by_external_id
    -- params: integer external_territorial_authority_id, varchar territorial_authority, varchar geometry
    -- return: integer territorial_authority_id

-- territorial_authority_attribute_update_building_outlines
    -- params: integer[] territorial_authority_id
    -- return: integer building_outline_id

-- territorial_authority_geometry_update_building_outlines
    -- params: varchar shape
    -- return: integer building_outline_id

----------------------------------------------------------------------------------------------

-- Functions

-- territorial_authority_grid_intersect_polygon (id of the TA that has the most overlap)
    -- params: p_polygon_geometry, geometry
    -- return: integer territorial_authority_id

CREATE OR REPLACE FUNCTION buildings_reference.territorial_authority_grid_intersect_polygon(
    p_polygon_geometry geometry
)
RETURNS integer AS
$$

    SELECT territorial_authority_id
    FROM buildings_reference.territorial_authority_grid
    WHERE ST_DWithin(p_polygon_geometry, shape, 1000)
    ORDER BY
          ST_Area(ST_Intersection(p_polygon_geometry, shape)) / ST_Area(shape) DESC
        , ST_Distance(p_polygon_geometry, shape) ASC
    LIMIT 1;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.territorial_authority_grid_intersect_polygon(geometry) IS
'Returns id of the TA Grid that has the most overlap';

-- territorial_authority_intersect_polygon (id of the TA that has the most overlap)
    -- params: p_polygon_geometry geometry
    -- return: integer territorial_authority_id

CREATE OR REPLACE FUNCTION buildings_reference.territorial_authority_intersect_polygon(
    p_polygon_geometry geometry
)
RETURNS integer AS
$$

    SELECT territorial_authority_id
    FROM buildings_reference.territorial_authority
    WHERE shape && ST_Expand(p_polygon_geometry, 1000)
    ORDER BY
          ST_Area(ST_Intersection(p_polygon_geometry, shape)) / ST_Area(shape) DESC
        , ST_Distance(p_polygon_geometry, shape) ASC
    LIMIT 1;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.territorial_authority_intersect_polygon(geometry) IS
'Return id of territorial authority with most overlap';

DROP FUNCTION IF EXISTS buildings_reference.territorial_auth_delete_areas();
DROP FUNCTION IF EXISTS buildings_reference.territorial_auth_insert_areas();
DROP FUNCTION IF EXISTS buildings_reference.territorial_auth_update_areas();


-- territorial_authority_delete_by_external_id
    -- params: integer external_territorial_authority_id
    -- return: integer territorial_authority_id
CREATE OR REPLACE FUNCTION buildings_reference.territorial_authority_delete_by_external_id(integer)
RETURNS integer AS
$$

    DELETE FROM buildings_reference.territorial_authority
    WHERE external_territorial_authority_id = $1
    RETURNING territorial_authority_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.territorial_authority_delete_by_external_id(integer) IS
'Delete from territorial_authority table by external id';


-- territorial_authority_insert
    -- params: integer external_territorial_authority_id, varchar territorial_authority, varchar geometry
    -- return: integer territorial_authority_id
CREATE OR REPLACE FUNCTION buildings_reference.territorial_authority_insert(integer, varchar, varchar)
RETURNS integer AS
$$

    INSERT INTO buildings_reference.territorial_authority (external_territorial_authority_id, name, shape)
    VALUES ($1, $2, ST_SetSRID(ST_GeometryFromText($3), 2193))
    RETURNING territorial_authority_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.territorial_authority_insert(integer, varchar, varchar) IS
'Insert new entry into territorial_authority table';


-- territorial_authority_update_by_external_id
    -- params: integer external_territorial_authority_id, varchar territorial_authority, varchar geometry
    -- return: integer territorial_authority_id
CREATE OR REPLACE FUNCTION buildings_reference.territorial_authority_update_by_external_id(integer, varchar, varchar)
RETURNS integer AS
$$

    UPDATE buildings_reference.territorial_authority
    SET name = $2,
        shape = ST_SetSRID(ST_GeometryFromText($3), 2193)
    WHERE external_territorial_authority_id = $1
    RETURNING territorial_authority_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.territorial_authority_update_by_external_id(integer, varchar, varchar) IS
'Update territorial_authority table by external id';


-- territorial_authority_attribute_update_building_outlines
    -- params: integer[] territorial_authority_id
    -- return: integer building_outline_id
CREATE OR REPLACE FUNCTION buildings_reference.territorial_authority_attribute_update_building_outlines(integer[])
RETURNS integer AS
$$
    UPDATE buildings.building_outlines
    SET last_modified = NOW()
    WHERE territorial_authority_id = ANY($1)
    RETURNING building_outline_id;
$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.territorial_authority_attribute_update_building_outlines(integer[]) IS
'Update building_outlines last_modified value as territorial_authority attribute was updated';


-- territorial_authority_geometry_update_building_outlines
    -- params: varchar shape
    -- return: integer building_outline_id
CREATE OR REPLACE FUNCTION buildings_reference.territorial_authority_geometry_update_building_outlines(varchar)
RETURNS integer AS
$$
	WITH sub_tas AS (
		SELECT ST_Subdivide(ST_SetSRID(ST_GeometryFromText($1), 2193)) AS shape
	)
	UPDATE buildings.building_outlines bo
	SET territorial_authority_id = buildings_reference.territorial_authority_grid_intersect_polygon(bo.shape),
		last_modified = NOW()
	FROM sub_tas ta
	WHERE ST_Intersects(bo.shape, ta.shape)
	AND territorial_authority_id != buildings_reference.territorial_authority_grid_intersect_polygon(bo.shape)
	RETURNING building_outline_id;
$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.territorial_authority_geometry_update_building_outlines(varchar) IS
'Update building_outlines territorial_authority_id value where building_outlines intersects with updated territorial_authority';

COMMIT;
