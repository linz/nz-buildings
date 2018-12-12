--------------------------------------------
-- buildings_reference.town_city

-- Functions

-- town_city_intersect_polygon (id of the town/city that has the most overlap)
    -- params: p_polygon_geometry geometry
    -- return: integer town_city_id

-- bulk_load_outlines_update_town_city (Replace the town/city values with the intersection)
    -- params: integer supplied_dataset_id
    -- return: count(integer) number of outlines updated

--------------------------------------------

-- Functions:

-- town_city_intersect_polygon (id of the town/city that has the most overlap)
    -- params: p_polygon_geometry geometry
    -- return: integer town_city_id
CREATE OR REPLACE FUNCTION buildings_reference.town_city_intersect_polygon(
    p_polygon_geometry geometry
)
RETURNS integer AS
$$

    SELECT town_city_id
    FROM buildings_reference.town_city
    WHERE ST_Intersects(shape, p_polygon_geometry)
    ORDER BY
          ST_Area(ST_Intersection(p_polygon_geometry, shape)) DESC
    LIMIT 1;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.town_city_intersect_polygon(geometry) IS
'Return id of town/city with most overlap';

-- bulk_load_outlines_update_town_city (Replace the town/city values with the intersection)
    -- params: integer supplied_dataset_id
    -- return: count(integer) number of outlines updated
CREATE OR REPLACE FUNCTION buildings_reference.bulk_load_outlines_update_town_city(integer)
RETURNS integer AS
$$

    WITH update_town_city AS (
        UPDATE buildings_bulk_load.bulk_load_outlines outlines
        SET town_city_id = town_city_intersect.town_city_intersect_polygon
        FROM (
            SELECT
                  buildings_reference.town_city_intersect_polygon(outlines.shape)
                , outlines.bulk_load_outline_id
            FROM buildings_bulk_load.bulk_load_outlines outlines
        ) town_city_intersect
        WHERE outlines.bulk_load_outline_id = town_city_intersect.bulk_load_outline_id
        AND outlines.supplied_dataset_id = $1
        RETURNING *
    )
    SELECT count(*)::integer FROM update_town_city;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.bulk_load_outlines_update_town_city(integer) IS
'Replace the town/city values with the intersection';
