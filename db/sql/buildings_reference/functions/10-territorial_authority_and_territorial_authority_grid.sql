----------------------------------------------------------------------------------------------
-- buildings_reference.territorial_authority && buildings_reference.territorial_authority_grid

-- Functions

-- territorial_authority_grid_intersect_polygon (id of the TA that has the most overlap)
    -- params: p_polygon_geometry, geometry
    -- return: integer territorial_authority_id

-- territorial_authority_intersect_polygon (id of the TA that has the most overlap)
    -- params: p_polygon_geometry geometry
    -- return: integer territorial_authority_id

-- bulk_load_outlines_update_territorial_authority (Replace the TA values with the intersection result)
    -- params: integer supplied_dataset_id
    -- return: count(integer) number of outlines updated

-- bulk_load_outlines_update_all_territorial_authorities (Replace the TA values with the intersection result)
    -- params:
    -- return: count(integer) number of outlines updated

-- building_outlines_update_territorial_authority (Replace the TA values with the intersection result)
    -- params:
    -- return: count(integer) number of outlines updated

-- territorial_auth_delete_areas(delete areas no long in admin_bdys)
    -- params:
    -- return: integer count of TAs deleted

-- territorial_auth_insert_areas(insert new areas from admin_bdys)
    -- params:
    -- return: integer count of new areas added

-- territorial_auth_update_areas(update geometries based on admin_bdys)
    -- params:
    -- return: integer count of areas updated

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


-- bulk_load_outlines_update_territorial_authority (Replace the TA values with the intersection result)
    -- params: integer supplied_dataset_id
    -- return: count(integer) number of outlines updated
CREATE OR REPLACE FUNCTION buildings_reference.bulk_load_outlines_update_territorial_authority(integer)
RETURNS integer AS
$$

    WITH update_territorial_auth AS (
        UPDATE buildings_bulk_load.bulk_load_outlines outlines
        SET territorial_authority_id = territorial_authority_intersect.territorial_authority_intersect_polygon
        FROM (
            SELECT
                  buildings_reference.territorial_authority_intersect_polygon(outlines.shape)
                , outlines.bulk_load_outline_id
            FROM buildings_bulk_load.bulk_load_outlines outlines
        ) territorial_authority_intersect
        WHERE outlines.bulk_load_outline_id = territorial_authority_intersect.bulk_load_outline_id
        AND outlines.supplied_dataset_id = $1
        RETURNING *
    )
    SELECT count(*)::integer FROM update_territorial_auth;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.bulk_load_outlines_update_territorial_authority(integer) IS
'Replace the TA values with the intersection result';

-- bulk_load_outlines_update_all_territorial_authorities (Replace the TA values with the intersection result)
    -- params:
    -- return: count(integer) number of outlines updated
CREATE OR REPLACE FUNCTION buildings_reference.bulk_load_outlines_update_all_territorial_authorities()
RETURNS integer AS
$$

    WITH update_territorial_auth AS (
        UPDATE buildings_bulk_load.bulk_load_outlines outlines
        SET territorial_authority_id = territorial_authority_intersect.territorial_authority_intersect_polygon
        FROM (
            SELECT
                  buildings_reference.territorial_authority_intersect_polygon(outlines.shape)
                , outlines.bulk_load_outline_id
            FROM buildings_bulk_load.bulk_load_outlines outlines
        ) territorial_authority_intersect
        WHERE outlines.bulk_load_outline_id = territorial_authority_intersect.bulk_load_outline_id
        RETURNING *
    )
    SELECT count(*)::integer FROM update_territorial_auth;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.bulk_load_outlines_update_all_territorial_authorities() IS
'Replace the TA values with the intersection result for all buildings in bulk_load_outlines';

-- building_outlines_update_territorial_authority (Replace the TA values with the intersection result)
    -- params:
    -- return: count(integer) number of outlines updated
CREATE OR REPLACE FUNCTION buildings_reference.building_outlines_update_territorial_authority()
RETURNS integer AS
$$

    WITH update_territorial_auth AS (
        UPDATE buildings.building_outlines outlines
        SET territorial_authority_id = territorial_authority_intersect.territorial_authority_intersect_polygon
        FROM (
            SELECT
                  buildings_reference.territorial_authority_intersect_polygon(outlines.shape)
                , outlines.building_outline_id
            FROM buildings.building_outlines outlines
        ) territorial_authority_intersect
        WHERE outlines.building_outline_id = territorial_authority_intersect.building_outline_id
        RETURNING *
    )
    SELECT count(*)::integer FROM update_territorial_auth;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.building_outlines_update_territorial_authority() IS
'Replace the TA values with the intersection result for all buildings in building_outlines';

-- Update Territorial Authority table:

-- territorial_auth_delete_areas(delete areas no long in admin_bdys)
    -- params:
    -- return: integer count of TAs deleted
CREATE OR REPLACE FUNCTION buildings_reference.territorial_auth_delete_areas()
RETURNS integer AS
$$
    WITH delete_ta AS (
        DELETE FROM buildings_reference.territorial_authority
        WHERE external_territorial_authority_id NOT IN (SELECT DISTINCT
            ogc_fid
          FROM admin_bdys.territorial_authority)
        RETURNING *
    )
    SELECT count(*)::integer FROM delete_ta

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.territorial_auth_delete_areas() IS
'Function to delete the attributes in the buildings_reference territorial_authority table that are not in the admin_bdys schema.';

-- territorial_auth_insert_areas(insert new areas from admin_bdys)
    -- params:
    -- return: integer count of new areas added
CREATE OR REPLACE FUNCTION buildings_reference.territorial_auth_insert_areas()
RETURNS integer AS
$$
    WITH insert_ta AS (
        INSERT INTO buildings_reference.territorial_authority (external_territorial_authority_id, name, shape)
          SELECT
            ogc_fid,
            name,
            ST_SetSRID(ST_Transform(shape, 2193), 2193)
          FROM admin_bdys.territorial_authority
          WHERE ogc_fid NOT IN (SELECT
            external_territorial_authority_id
          FROM buildings_reference.territorial_authority)
        RETURNING *
    )
    SELECT count(*)::integer FROM insert_ta;
$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.territorial_auth_insert_areas() IS
'Function to insert new territorial authority areas into the buildings_reference.territorial_authority table.';

-- territorial_auth_update_areas(update geometries based on admin_bdys)
    -- params:
    -- return: integer count of areas updated
CREATE OR REPLACE FUNCTION buildings_reference.territorial_auth_update_areas()
RETURNS integer AS
$$
    WITH update_ta AS (
        UPDATE buildings_reference.territorial_authority bta
        SET name = ata.name,
            shape = ST_SetSRID(ST_Transform(ata.shape, 2193), 2193)
        FROM admin_bdys.territorial_authority ata
        WHERE bta.external_territorial_authority_id IN
            (SELECT ogc_fid
             FROM admin_bdys.territorial_authority ata
             JOIN buildings_reference.territorial_authority bta ON ogc_fid = external_territorial_authority_id
             WHERE NOT st_equals(bta.shape, ST_SetSRID(ST_Transform(ata.shape, 2193), 2193))
               OR bta.name != ata.name)
        RETURNING *
    )
    SELECT count(*)::integer FROM update_ta;
$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.territorial_auth_update_areas() IS
'Function to update territorial_authority areas that have either name or geometry changes';
