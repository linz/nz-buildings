--------------------------------------------
-- buildings_reference.suburb_locality

-- Functions
-- suburb_locality_intersect_polygon (id of suburb with most overlap)
    -- param: p_polygon_geometry geometry
    -- returns: integer suburb_locality_id
-- bulk_load_outlines_update_suburb (replace suburb values with the intersection result)
    -- param: integer supplied_dataset_id
    -- returns: count(integer) number of building outlines updated
--------------------------------------------

-- Functions

-- suburb_locality_intersect_polygon (id of suburb with most overlap)
    -- param: p_polygon_geometry geometry
    -- returns: integer suburb_locality_id
CREATE OR REPLACE FUNCTION buildings.suburb_locality_intersect_polygon(
    p_polygon_geometry geometry
)
RETURNS integer AS
$$

    SELECT suburb_locality_id
    FROM buildings_reference.suburb_locality
    WHERE shape && ST_Expand(p_polygon_geometry, 1000)
    ORDER BY
          ST_Area(ST_Intersection(p_polygon_geometry, shape)) / ST_Area(shape) DESC
        , ST_Distance(p_polygon_geometry, shape) ASC
    LIMIT 1;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings.suburb_locality_intersect_polygon(geometry) IS
'Return id of suburb/locality with most overlap';


-- bulk_load_outlines_update_suburb (replace suburb values with the intersection result)
    -- param: integer supplied_dataset_id
    -- returns: count(integer) number of building outlines updated
CREATE OR REPLACE FUNCTION buildings.bulk_load_outlines_update_suburb(integer)
RETURNS integer AS
$$

    WITH update_suburb AS (
        UPDATE buildings_bulk_load.bulk_load_outlines outlines
        SET suburb_locality_id = suburb_locality_intersect.suburb_locality_intersect_polygon
        FROM (
            SELECT
                  buildings.suburb_locality_intersect_polygon(outlines.shape)
                , outlines.bulk_load_outline_id
            FROM buildings_bulk_load.bulk_load_outlines outlines
        ) suburb_locality_intersect
        WHERE outlines.bulk_load_outline_id = suburb_locality_intersect.bulk_load_outline_id
        AND outlines.supplied_dataset_id = $1
        RETURNING *
    )
    SELECT count(*)::integer FROM update_suburb;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings.bulk_load_outlines_update_suburb(integer) IS
'Replace suburb values with the intersection result';
