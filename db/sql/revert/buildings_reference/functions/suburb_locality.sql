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

    SELECT suburb_locality_id
    FROM buildings_reference.suburb_locality
    WHERE shape && ST_Expand(p_polygon_geometry, 1000)
    ORDER BY
          ST_Area(ST_Intersection(p_polygon_geometry, shape)) DESC
        , ST_Distance(p_polygon_geometry, shape) ASC
    LIMIT 1;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.suburb_locality_intersect_polygon(geometry) IS
'Return id of suburb/locality with most overlap';

DROP FUNCTION IF EXISTS buildings_reference.suburb_locality_delete_by_external_id(integer);

DROP FUNCTION IF EXISTS buildings_reference.suburb_locality_insert(integer, varchar, varchar, varchar);

DROP FUNCTION IF EXISTS buildings_reference.suburb_locality_update_by_external_id(integer, varchar, varchar, varchar);

DROP FUNCTION IF EXISTS buildings_reference.suburb_locality_attribute_update_building_outlines(integer[]);

DROP FUNCTION IF EXISTS buildings_reference.suburb_locality_geometry_update_building_outlines(varchar);

COMMIT;
