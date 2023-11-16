-- Deploy nz-buildings:buildings_reference/functions/town_city to pg

BEGIN;

--------------------------------------------
-- buildings_reference.town_city

-- Functions

-- town_city_intersect_polygon (id of the town/city that has the most overlap)
    -- params: p_polygon_geometry geometry
    -- return: integer town_city_id

-- town_city_delete_removed_areas (removed from table areas not in admin_byds)
    -- params:
    -- return: integer list of town_cities deleted

-- town_city_insert_new_areas (insert new areas from admin_bdys)
    -- params:
    -- return: integer list of outlines inserted

-- town_city_update_areas(update geometries based on those in admin_bdys)
    -- params:
    -- return: integer list of areas updated

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
    ORDER BY ST_Area(ST_Intersection(p_polygon_geometry, shape)) DESC
    LIMIT 1;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.town_city_intersect_polygon(geometry) IS
'Return id of town/city with most overlap';

-- update town_city table functions:

-- town_city_delete_removed_areas (removed from table areas not in admin_byds)
    -- params:
    -- return: integer list of town_cities deleted

CREATE OR REPLACE FUNCTION buildings_reference.town_city_delete_removed_areas()
RETURNS integer[] AS
$$

    WITH delete_town AS (
        DELETE FROM buildings_reference.town_city
        WHERE external_city_id NOT IN (
            SELECT DISTINCT city_id
            FROM admin_bdys.nz_locality
            WHERE city_id IS NOT NULL
        )
        RETURNING *
    )
    SELECT ARRAY(SELECT town_city_id FROM delete_town);

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.town_city_delete_removed_areas() IS
'Function to delete from the buildings_reference town city table the areas that have been removed in the admin_bdys schema';

-- town_city_insert_new_areas (insert new areas from admin_bdys)
    -- params:
    -- return: integer list of outlines inserted

CREATE OR REPLACE FUNCTION buildings_reference.town_city_insert_new_areas()
RETURNS integer[] AS
$$

    WITH insert_town AS (
        INSERT INTO buildings_reference.town_city (external_city_id, name, shape)
            SELECT
                  subquery.city_id
                , subquery.city_name
                , ST_SetSRID(ST_Transform(subquery.shape, 2193), 2193)
            FROM (
                SELECT
                      city_id
                    , city_name
                    , ST_Multi(ST_Union(nzl.shape)) AS shape
                FROM admin_bdys.nz_locality AS nzl
                WHERE city_id != 0
                AND city_id NOT IN (
                    SELECT external_city_id
                    FROM buildings_reference.town_city
                )
            GROUP BY city_id, city_name
            ) AS subquery
        RETURNING *
    )
    SELECT ARRAY(
        SELECT town_city_id
        FROM insert_town
    );

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.town_city_insert_new_areas() IS
'Function to insert from the admin_bdys schema new areas not in the buildings_reference town city table';

-- town_city_update_areas(update geometries based on those in admin_bdys)
    -- params:
    -- return: integer list of areas updated

CREATE OR REPLACE FUNCTION buildings_reference.town_city_update_areas()
RETURNS integer[] AS
$$

    WITH update_town AS (
        UPDATE buildings_reference.town_city
        SET
              name = subquery.city_name
            , shape = ST_SetSRID(ST_Transform(subquery.shape, 2193), 2193)
        FROM (
            SELECT
                  city_id
                , city_name
                , ST_Multi(ST_Union(nzl.shape)) AS shape
            FROM admin_bdys.nz_locality AS nzl
            WHERE city_id != 0
            GROUP BY city_id, city_name
        ) AS subquery
        WHERE buildings_reference.town_city.external_city_id = subquery.city_id
        AND (   NOT ST_Equals(ST_SetSRID(ST_Transform(subquery.shape, 2193), 2193), buildings_reference.town_city.shape)
             OR city_name != buildings_reference.town_city.name
        )
        RETURNING *
    )
    SELECT ARRAY(
        SELECT town_city_id
        FROM update_town
    );

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.town_city_update_areas() IS
'Function to update the id, names and geometries of the town city';

COMMIT;
