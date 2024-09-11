-- Deploy nz-buildings:buildings_reference/functions/suburb_locality to pg

BEGIN;

--------------------------------------------
-- buildings_reference.suburb_locality

-- Functions

-- suburb_locality_intersect_polygon (id of suburb with most overlap)
    -- params: p_polygon_geometry geometry
    -- return: integer suburb_locality_id

-- suburb_locality_delete_by_external_id
    -- params: integer external_suburb_locality_id
    -- return: integer suburb_locality_id

-- suburb_locality_insert
    -- params: integer external_suburb_locality_id, varchar suburb_locality, varchar town_city, varchar geometry
    -- return: integer suburb_locality_id

-- suburb_locality_update_by_external_id
    -- params: integer external_suburb_locality_id, varchar suburb_locality, varchar town_city, varchar geometry
    -- return: integer suburb_locality_id

-- suburb_locality_update_building_outlines
    -- params: integer[] suburb_locality_id, integer[] suburb_locality_id
    -- return: integer building_outline_id
    
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


-- suburb_locality_delete_by_external_id
    -- params: integer external_suburb_locality_id
    -- return: integer suburb_locality_id
CREATE OR REPLACE FUNCTION buildings_reference.suburb_locality_delete_by_external_id(integer)
RETURNS integer AS
$$

    DELETE FROM buildings_reference.suburb_locality
    WHERE external_suburb_locality_id = $1
    RETURNING suburb_locality_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.suburb_locality_delete_by_external_id(integer) IS
'Delete from suburb_locality table by external id';


-- suburb_locality_insert
    -- params: integer external_suburb_locality_id, varchar suburb_locality, varchar town_city, varchar geometry
    -- return: integer suburb_locality_id
CREATE OR REPLACE FUNCTION buildings_reference.suburb_locality_insert(integer, varchar, varchar, varchar)
RETURNS integer AS
$$

    INSERT INTO buildings_reference.suburb_locality (external_suburb_locality_id, suburb_locality, town_city, shape)
    VALUES ($1, $2, $3, ST_SetSRID(ST_GeometryFromText($4), 2193))
    RETURNING suburb_locality_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.suburb_locality_insert(integer, varchar, varchar, varchar) IS
'Insert new entry into suburb_locality table';


-- suburb_locality_update_by_external_id
    -- params: integer external_suburb_locality_id, varchar suburb_locality, varchar town_city, varchar geometry
    -- return: integer suburb_locality_id
CREATE OR REPLACE FUNCTION buildings_reference.suburb_locality_update_by_external_id(integer, varchar, varchar, varchar)
RETURNS integer AS
$$

    UPDATE buildings_reference.suburb_locality
    SET suburb_locality = $2,
        town_city = $3,
        shape = ST_SetSRID(ST_GeometryFromText($4), 2193)
    WHERE external_suburb_locality_id = $1
    RETURNING suburb_locality_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.suburb_locality_update_by_external_id(integer, varchar, varchar, varchar) IS
'Update suburb_locality table by external id';


-- suburb_locality_update_building_outlines
    -- params: integer[] suburb_locality_id, integer[] suburb_locality_id
    -- return: integer building_outline_id
CREATE OR REPLACE FUNCTION buildings_reference.suburb_locality_update_building_outlines(integer[], integer[])
RETURNS integer AS
$$
    UPDATE buildings.building_outlines
    SET suburb_locality_id = buildings_reference.suburb_locality_intersect_polygon(shape),
        last_modified = NOW()
    WHERE (
            suburb_locality_id = ANY($1)
        AND suburb_locality_id != buildings_reference.suburb_locality_intersect_polygon(shape)
    )
    OR suburb_locality_id = ANY($2)
    RETURNING building_outline_id;
$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.suburb_locality_update_building_outlines(integer[], integer[]) IS
'Update building_outlines suburb_locality_id value using suburb_locality table';


COMMIT;
