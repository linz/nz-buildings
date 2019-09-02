-- Revert nz-buildings:buildings_reference/functions/change_reference_name_col_insert from pg

BEGIN;

-- Bivouac

DROP FUNCTION IF EXISTS buildings_reference.bivouac_points_insert(integer, varchar, varchar);

DROP FUNCTION IF EXISTS buildings_reference.bivouac_points_update_by_external_id(integer, varchar, varchar);


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


-- Hut

DROP FUNCTION IF EXISTS buildings_reference.hut_points_insert(integer, varchar, varchar);

DROP FUNCTION IF EXISTS buildings_reference.hut_points_update_by_external_id(integer, varchar, varchar);


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


-- Protected Area

DROP FUNCTION IF EXISTS buildings_reference.protected_areas_polygons_insert(integer, varchar, varchar);

DROP FUNCTION IF EXISTS buildings_reference.protected_areas_polygons_update_by_external_id(integer, varchar, varchar);


-- protected_areas_polygons_insert
    -- params: integer external_protected_areas_polygon_id, varchar geometry
    -- return: integer protected_areas_polygon_id

CREATE OR REPLACE FUNCTION buildings_reference.protected_areas_polygons_insert(integer, varchar)
RETURNS integer AS
$$

    INSERT INTO buildings_reference.protected_areas_polygons (external_protected_areas_polygon_id, shape)
    VALUES ($1, ST_SetSRID(ST_GeometryFromText($2), 2193))
    RETURNING protected_areas_polygon_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.protected_areas_polygons_insert(integer, varchar) IS
'Insert new entry into protected_areas_polygons table';


-- protected_areas_polygons_update_shape_by_external_id
    -- params: integer external_protected_areas_polygon_id, varchar geometry
    -- return: integer protected_areas_polygon_id

CREATE OR REPLACE FUNCTION buildings_reference.protected_areas_polygons_update_shape_by_external_id(integer, varchar)
RETURNS integer AS
$$

    UPDATE buildings_reference.protected_areas_polygons
    SET shape = ST_SetSRID(ST_GeometryFromText($2), 2193)
    WHERE external_protected_areas_polygon_id = $1
    RETURNING protected_areas_polygon_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.protected_areas_polygons_update_shape_by_external_id(integer, varchar) IS
'Update geometry of protected areas based on external_protected_areas_polygon_id';


-- Shelter

DROP FUNCTION IF EXISTS buildings_reference.shelter_points_insert(integer, varchar, varchar);

DROP FUNCTION IF EXISTS buildings_reference.shelter_points_update_by_external_id(integer, varchar, varchar);


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
