-- Revert nz-buildings:buildings_reference/functions/update_suburb_locality_changed_deleted_buildings from pg

BEGIN;

DROP FUNCTION buildings_reference.building_outlines_update_changed_and_deleted_suburb();

DROP FUNCTION buildings_reference.building_outlines_update_added_suburb();

-- suburb_locality_delete_removed_areas (delete suburbs that are no longer is admin_bdys)
    -- params:
    -- return: integer list of outlines deleted

CREATE OR REPLACE FUNCTION buildings_reference.suburb_locality_delete_removed_areas()
RETURNS integer[] AS
$$

    WITH delete_suburb AS (
        DELETE FROM buildings_reference.suburb_locality
        WHERE external_suburb_locality_id NOT IN (
            SELECT id
            FROM admin_bdys.nz_locality
        )
        RETURNING *
    )
    SELECT ARRAY(
        SELECT suburb_locality_id
        FROM delete_suburb
    );

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.suburb_locality_delete_removed_areas() IS
'Function to delete from the buildings_reference suburb locality table the areas that have been removed in the admin_bdys schema';

-- suburb_locality_insert_new_areas (insert new areas from admin_bdys)
    -- params:
    -- return: integer list of areas inserted

CREATE OR REPLACE FUNCTION buildings_reference.suburb_locality_insert_new_areas()
RETURNS integer[] AS
$$

    WITH insert_suburb AS (
        INSERT INTO buildings_reference.suburb_locality (
              external_suburb_locality_id
            , suburb_4th
            , suburb_3rd
            , suburb_2nd
            , suburb_1st
            , shape
        )
        SELECT
              id
            , suburb_4th
            , suburb_3rd
            , suburb_2nd
            , suburb_1st
            , ST_SetSRID(ST_Transform(shape, 2193), 2193)
        FROM admin_bdys.nz_locality
        WHERE type in ('ISLAND','LOCALITY','PARK_RESERVE','SUBURB')
        AND id NOT IN (
            SELECT external_suburb_locality_id
            FROM buildings_reference.suburb_locality
        )
        RETURNING *
    )
    SELECT ARRAY(
        SELECT suburb_locality_id
        FROM insert_suburb
    );

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.suburb_locality_insert_new_areas() IS
'Function to insert from the admin_bdys schema new areas not in the buildings_reference suburb locality table';

-- suburb_locality_update_suburb_locality (update geometries based on those in admin_bdys)
    -- params:
    -- return: integer list of areas updated

CREATE OR REPLACE FUNCTION buildings_reference.suburb_locality_update_suburb_locality()
RETURNS integer[] AS
$$

    WITH update_suburb AS (
        UPDATE buildings_reference.suburb_locality bsl
        SET
              suburb_4th = nzl.suburb_4th
            , suburb_3rd = nzl.suburb_3rd
            , suburb_2nd = nzl.suburb_2nd
            , suburb_1st = nzl.suburb_1st
            , shape = ST_SetSRID(ST_Transform(nzl.shape, 2193), 2193)
        FROM admin_bdys.nz_locality nzl
        WHERE bsl.external_suburb_locality_id = nzl.id
        AND (    NOT ST_Equals(ST_SetSRID(ST_Transform(nzl.shape, 2193), 2193), bsl.shape)
              OR nzl.suburb_4th != bsl.suburb_4th
              OR nzl.suburb_3rd != bsl.suburb_3rd
              OR nzl.suburb_2nd != bsl.suburb_2nd
              OR nzl.suburb_1st != bsl.suburb_1st
        )
        RETURNING *
    )
    SELECT ARRAY(SELECT suburb_locality_id FROM update_suburb);

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.suburb_locality_update_suburb_locality() IS
'Function to update the attributes in the buildings_reference suburb locality table from the admin_bdys schema';

-- building_outlines_update_suburb (replace suburb values with the intersection result)
    -- params: integer[] list of suburb localities building must be within
    -- return: integer count of number of building outlines updated

CREATE OR REPLACE FUNCTION buildings.building_outlines_update_suburb(integer[])
RETURNS integer AS
$$

    WITH update_suburb AS (
        UPDATE buildings.building_outlines outlines
        SET suburb_locality_id = suburb_locality_intersect.suburb_locality_intersect_polygon
        FROM (
            SELECT
                  buildings_reference.suburb_locality_intersect_polygon(outlines.shape)
                , outlines.building_outline_id
            FROM buildings.building_outlines outlines
        ) suburb_locality_intersect
        WHERE outlines.building_outline_id = suburb_locality_intersect.building_outline_id
        AND suburb_locality_id = ANY($1)
        RETURNING *
    )
    SELECT count(*)::integer FROM update_suburb;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings.building_outlines_update_suburb(integer[]) IS
'Replace suburb values with the intersection result of buildings in the building_outlines table';

-- bulk_load_outlines_update_all_suburbs (replace all suburb values with the intersection result)
    -- params: integer[] list of suburb localities building must be within
    -- return: count(integer) number of building outlines updated

CREATE OR REPLACE FUNCTION buildings_bulk_load.bulk_load_outlines_update_all_suburbs(integer[])
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
        AND suburb_locality_id = ANY($1)
        RETURNING *
    )
    SELECT count(*)::integer FROM update_suburb;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_bulk_load.bulk_load_outlines_update_all_suburbs(integer[]) IS
'Replace suburb values with the intersection result of all buildings in the bulk_load_outlines table';

COMMIT;
