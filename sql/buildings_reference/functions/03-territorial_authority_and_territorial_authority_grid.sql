----------------------------------------------------------------------------------------------
-- buildings_reference.territorial_authority && buildings_reference.territorial_authority_grid

-- Functions
-- territorial_authority_intersect_polygon (id of the TA that has the most overlap)
    -- param: p_polygon_geometry geometry
    -- return: integer territorial_authority_id
-- bulk_load_outlines_update_territorial_authority (Replace the TA values with the intersection result)
    -- param: integer supplied_dataset_id
    -- return: count(integer) number of outlines updated
-- territorial_authority_grid_intersect_polygon (id of the TA that has the most overlap)
    -- param: p_polygon_geometry, geometry
    -- return: integer territorial_authority_id
----------------------------------------------------------------------------------------------

-- Functions

-- territorial_authority_intersect_polygon (id of the TA that has the most overlap)
    -- param: p_polygon_geometry geometry
    -- return: integer territorial_authority_id
CREATE OR REPLACE FUNCTION buildings.territorial_authority_intersect_polygon(
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

COMMENT ON FUNCTION buildings.territorial_authority_intersect_polygon(geometry) IS
'Return id of territorial authority with most overlap';


-- bulk_load_outlines_update_territorial_authority (Replace the TA values with the intersection result)
    -- param: integer supplied_dataset_id
    -- return: count(integer) number of outlines updated
CREATE OR REPLACE FUNCTION buildings.bulk_load_outlines_update_territorial_authority(integer)
RETURNS integer AS
$$

    WITH update_territorial_auth AS (
        UPDATE buildings_bulk_load.bulk_load_outlines outlines
        SET territorial_authority_id = territorial_authority_intersect.territorial_authority_intersect_polygon
        FROM (
            SELECT
                  buildings.territorial_authority_intersect_polygon(outlines.shape)
                , outlines.bulk_load_outline_id
            FROM buildings_bulk_load.bulk_load_outlines outlines
        ) territorial_authority_intersect
        WHERE outlines.bulk_load_outline_id = territorial_authority_intersect.bulk_load_outline_id
        AND outlines.supplied_dataset_id = $1
        RETURNING $1
    )
    SELECT count(*)::integer FROM update_territorial_auth;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings.bulk_load_outlines_update_territorial_authority(integer) IS
'Replace the TA values with the intersection result';


-- territorial_authority_grid_intersect_polygon (id of the TA that has the most overlap)
    -- param: p_polygon_geometry, geometry
    -- return: integer territorial_authority_id
CREATE OR REPLACE FUNCTION buildings.territorial_authority_grid_intersect_polygon(
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

COMMENT ON FUNCTION buildings.territorial_authority_grid_intersect_polygon(geometry) IS
'Returns id of the TA Grid that has the most overlap';
