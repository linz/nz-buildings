-- Deploy nz-buildings:buildings_reference/functions/update_suburb_locality_changed_deleted_buildings to pg

BEGIN;

DROP FUNCTION buildings_reference.suburb_locality_insert_new_areas();
DROP FUNCTION buildings_reference.suburb_locality_update_suburb_locality();
DROP FUNCTION buildings_reference.suburb_locality_delete_removed_areas();
DROP FUNCTION buildings.building_outlines_update_suburb(integer[]);
DROP FUNCTION buildings_bulk_load.bulk_load_outlines_update_all_suburbs(integer[]);


-- building_outlines_update_changed_and_deleted_suburb (replace suburb values with the intersection result)
    -- params: 
    -- return: integer count of number of building outlines updated

CREATE OR REPLACE FUNCTION buildings_reference.building_outlines_update_changed_and_deleted_suburb()
RETURNS integer AS
$$
    -- Find new ids and geometry differences of changed 
    WITH changed_geometries
    AS (SELECT
        nzl.id AS new_external_id,
        bsl.suburb_locality_id AS new_id,
        ST_Difference(ST_Transform(nzl.shape, 2193),bsl.shape) AS shape
    FROM admin_bdys.nz_locality nzl,
        buildings_reference.suburb_locality bsl
    WHERE 
        bsl.external_suburb_locality_id = nzl.id
        AND (NOT ST_Equals(ST_Transform(nzl.shape, 2193), bsl.shape))
        AND (NOT st_isempty(ST_Difference(ST_Transform(nzl.shape, 2193),bsl.shape)))),
    
    -- Joins the difference and new ids with the old suburb_locality_id
    intersected_change
    AS (SELECT 
        bsl.external_suburb_locality_id AS old_id,
        cg.new_external_id,
        cg.new_id,
        cg.shape AS shape
    FROM buildings_reference.suburb_locality bsl,
         changed_geometries cg
    WHERE 
        (ST_Overlaps(cg.shape, bsl.shape) OR ST_Within(cg.shape, bsl.shape))
        AND bsl.external_suburb_locality_id != cg.new_external_id),
    
    -- Update the changed suburbs
    updated_suburbs 
    AS (UPDATE buildings_reference.suburb_locality bsl
        SET
              suburb_4th = nzl.suburb_4th
            , suburb_3rd = nzl.suburb_3rd
            , suburb_2nd = nzl.suburb_2nd
            , suburb_1st = nzl.suburb_1st
            , shape = ST_SetSRID(ST_Transform(nzl.shape, 2193), 2193)
        FROM admin_bdys.nz_locality nzl
        WHERE bsl.external_suburb_locality_id = nzl.id
        AND (NOT ST_Equals(ST_SetSRID(ST_Transform(nzl.shape, 2193), 2193), bsl.shape)
              OR nzl.suburb_4th != bsl.suburb_4th
              OR nzl.suburb_3rd != bsl.suburb_3rd
              OR nzl.suburb_2nd != bsl.suburb_2nd
              OR nzl.suburb_1st != bsl.suburb_1st
        )),
      
    -- Remove deleted suburbs
    deleted_suburbs 
    AS (DELETE FROM buildings_reference.suburb_locality
        WHERE external_suburb_locality_id NOT IN (
            SELECT id
            FROM admin_bdys.nz_locality
        )),
    
    -- Updates building outlines where:
      -- It's external id is an 'old id'
      -- It Overlaps or is Within the difference polygon for the 'old id'
      -- It overlaps the difference polygon by the largest proportion
    building_outline_updates
    AS (UPDATE 
        buildings.building_outlines b
        SET suburb_locality_id = buildings_reference.suburb_locality_intersect_polygon(b.shape)
    FROM 
    intersected_change ic, buildings_reference.suburb_locality bsl
    WHERE 
        b.suburb_locality_id = bsl.suburb_locality_id
        AND bsl.external_suburb_locality_id = ic.old_id
        AND (ST_Within(b.shape, ic.shape)
        OR ST_Overlaps(b.shape, ic.shape)
        )
        RETURNING *
        )

    SELECT count(*)::integer FROM building_outline_updates;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.building_outlines_update_changed_and_deleted_suburb() IS
'Replace suburb values with the intersection result of buildings in the building_outlines table';


-- building_outlines_update_added_suburb (replace suburb values with the intersection result)
    -- params: 
    -- return: integer count of number of building outlines updated

CREATE OR REPLACE FUNCTION buildings_reference.building_outlines_update_added_suburb()
RETURNS integer AS
$$
    -- add new suburbs to buildings_reference.suburb_locality
      -- (to get new suburb_locality_ids)
    WITH add_new_suburbs AS (
      INSERT INTO buildings_reference.suburb_locality (
        external_suburb_locality_id, suburb_4th,
        suburb_3rd, suburb_2nd, suburb_1st, shape
      )
      SELECT
        id, suburb_4th, suburb_3rd,
        suburb_2nd, suburb_1st,
        ST_Transform(shape, 2193)
      FROM 
        admin_bdys.nz_locality
      WHERE
        type IN ('ISLAND','LOCALITY','PARK_RESERVE','SUBURB')
        AND id NOT IN (
          SELECT
            external_suburb_locality_id
          FROM 
            buildings_reference.suburb_locality
        ) RETURNING *
    ),

    -- Find the 'old suburb locality ids' that overlap the new suburbs
    added_overlap AS (
      SELECT
        ans.suburb_locality_id as new_suburb_loc_id,
        bsl.suburb_locality_id as old_suburb_loc_id,
        ans.shape AS shape
      FROM
        add_new_suburbs ans,
        buildings_reference.suburb_locality bsl
      WHERE 
        (
          ST_Overlaps(bsl.shape, ans.shape)
          OR ST_Within(bsl.shape, ans.shape)
          OR ST_Contains(bsl.shape, ans.shape)
        )
        AND ans.suburb_locality_id != bsl.suburb_locality_id
    ),

    -- update building outlines where:
      -- they have a id that is an old id (that overlaps a new suburb)
      -- the building is within/overlaps the new suburb
      -- the building overlaps the new polygon by the largest proportion 
    update_building_outlines AS (
        UPDATE 
          buildings.building_outlines b
        SET 
          suburb_locality_id = buildings_reference.suburb_locality_intersect_polygon(b.shape) 
        FROM 
          added_overlap ao
        WHERE 
          b.suburb_locality_id = ao.old_suburb_loc_id
        RETURNING *
        )

    SELECT count(*)::integer FROM update_building_outlines;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.building_outlines_update_added_suburb() IS
'Insert new suburb localities and replace old suburb values with the intersection result in the building_outlines table';

COMMIT;
