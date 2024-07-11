-- Deploy nz-buildings:buildings_reference/functions/suburb_locality to pg

BEGIN;

--------------------------------------------
-- buildings_reference.suburb_locality

-- Functions

-- suburb_locality_intersect_polygon (id of suburb with most overlap)
    -- params: p_polygon_geometry geometry
    -- return: integer suburb_locality_id

--------------------------------------------

-- Functions

-- suburb_locality_intersect_polygon (id of suburb with most overlap)
    -- params: p_polygon_geometry geometry
    -- return: integer suburb_locality_id

CREATE OR REPLACE FUNCTION buildings_reference.suburb_locality_intersect_polygon(
    p_polygon_geometry geometry
)
RETURNS integer AS
$$
    -- Precaculate which (and how many) suburb_locality geometries the
    -- input geometry intersects with
    WITH intersecting_suburbs AS (
        SELECT suburb_locality_id, shape
        FROM buildings_reference.suburb_locality
        WHERE ST_Intersects(p_polygon_geometry, shape)
    ), intersecting_suburbs_count AS (
        SELECT COUNT(*) AS num_suburbs FROM intersecting_suburbs
    )

    SELECT
    -- If the input geometry does not intersect directly with any
    -- suburb_locality geometries, return the closest suburb_locality
    CASE WHEN intersecting_suburbs_count.num_suburbs = 0 THEN (
        SELECT suburb_locality_id FROM buildings_reference.suburb_locality
        WHERE ST_DWithin(p_polygon_geometry, shape, 1000)
        ORDER BY ST_Distance(p_polygon_geometry, shape) ASC
        LIMIT 1
    )
    -- If the input geometry intersects with exactly one suburb_locality
    -- geometry, return that
    WHEN intersecting_suburbs_count.num_suburbs = 1 THEN (
        SELECT suburb_locality_id FROM intersecting_suburbs LIMIT 1
    )
    -- If the input geometry intersects with more than one suburb_locality
    -- geometry, return the suburb_locality with the largest overlap
    ELSE (
        SELECT suburb_locality_id FROM intersecting_suburbs
        ORDER BY ST_Area(ST_Intersection(p_polygon_geometry, shape)) DESC
        LIMIT 1
    )
    END AS suburb_locality_id
    FROM intersecting_suburbs_count;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.suburb_locality_intersect_polygon(geometry) IS
'Return id of suburb/locality with most overlap';

COMMIT;
