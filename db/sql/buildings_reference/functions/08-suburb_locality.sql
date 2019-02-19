--------------------------------------------
-- buildings_reference.suburb_locality

-- Functions

-- suburb_locality_intersect_polygon (id of suburb with most overlap)
    -- params: p_polygon_geometry geometry
    -- return: integer suburb_locality_id

-- bulk_load_outlines_update_suburb (replace suburb values with the intersection result)
    -- params: integer supplied_dataset_id
    -- return: count(integer) number of building outlines updated

-- suburb_locality_delete_removed_areas (delete suburbs that are no longer is admin_bdys)
    -- params:
    -- return: integer number of outlines deleted

-- suburb_locality_insert_new_areas (insert new areas from admin_bdys)
    -- params:
    -- return: integer number of areas inserted

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
          ST_Area(ST_Intersection(p_polygon_geometry, shape)) / ST_Area(shape) DESC
        , ST_Distance(p_polygon_geometry, shape) ASC
    LIMIT 1;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.suburb_locality_intersect_polygon(geometry) IS
'Return id of suburb/locality with most overlap';


-- bulk_load_outlines_update_suburb (replace suburb values with the intersection result)
    -- params: integer supplied_dataset_id
    -- return: count(integer) number of building outlines updated
CREATE OR REPLACE FUNCTION buildings_reference.bulk_load_outlines_update_suburb(integer)
RETURNS integer AS
$$

    WITH update_suburb AS (
        UPDATE buildings_bulk_load.bulk_load_outlines outlines
        SET suburb_locality_id = suburb_locality_intersect.suburb_locality_intersect_polygon
        FROM (
            SELECT
                  buildings_reference.suburb_locality_intersect_polygon(outlines.shape)
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

COMMENT ON FUNCTION buildings_reference.bulk_load_outlines_update_suburb(integer) IS
'Replace suburb values with the intersection result';

-- update suburb_table_functions

-- suburb_locality_delete_removed_areas (delete suburbs that are no longer is admin_bdys)
    -- params:
    -- return: integer number of outlines deleted
CREATE OR REPLACE FUNCTION buildings_reference.suburb_locality_delete_removed_areas()
RETURNS integer AS
$$
    WITH delete_suburb AS (
        DELETE FROM buildings_reference.suburb_locality
        WHERE external_suburb_locality_id NOT
          IN (SELECT id
          FROM admin_bdys.nz_locality)
        RETURNING *
    )
    SELECT count(*)::integer FROM delete_suburb;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.suburb_locality_delete_removed_areas() IS
'Function to delete from the buildings_reference suburb locality table the areas that have been removed in the admin_bdys schema';

-- suburb_locality_insert_new_areas (insert new areas from admin_bdys)
    -- params:
    -- return: integer number of areas inserted
CREATE OR REPLACE FUNCTION buildings_reference.suburb_locality_insert_new_areas()
RETURNS integer AS
$$
    WITH insert_suburb AS (
        INSERT INTO buildings_reference.suburb_locality (external_suburb_locality_id, suburb_4th, suburb_3rd, suburb_2nd, suburb_1st, shape)
        SELECT
          id,
          suburb_4th,
          suburb_3rd,
          suburb_2nd,
          suburb_1st,
          ST_SetSRID(ST_Transform(shape, 2193), 2193)
        FROM admin_bdys.nz_locality
        WHERE id NOT IN (SELECT
          external_suburb_locality_id
        FROM buildings_reference.suburb_locality)
        RETURNING *
    )
    SELECT count(*)::integer FROM insert_suburb;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.suburb_locality_insert_new_areas() IS
'Function to insert from the admin_bdys schema new areas not in the buildings_reference suburb locality table';
