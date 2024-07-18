-- Deploy nz-buildings:buildings_reference/functions/update_suburb_locality_changed_deleted_buildings to pg

BEGIN;

-- building_outlines_update_changed_and_deleted_suburb (replace suburb values with the intersection result)
    -- params: 
    -- return: integer count of number of building outlines updated

CREATE OR REPLACE FUNCTION buildings_reference.building_outlines_update_changed_and_deleted_suburb()
RETURNS void AS
$$
BEGIN
    -- Find new ids and geometry differences of changed 
    CREATE TEMP TABLE changed_geometries AS
    SELECT
      nzl.id AS new_external_id,
      bsl.suburb_locality_id AS new_id,
      ST_Difference(ST_Transform(nzl.shape, 2193),bsl.shape) AS shape
    FROM 
      admin_bdys.nz_locality nzl,
      buildings_reference.suburb_locality bsl
    WHERE 
      bsl.external_suburb_locality_id = nzl.id
      AND (
        NOT ST_Equals(ST_Transform(nzl.shape, 2193), bsl.shape)
        )
      AND (
        NOT st_isempty(ST_Difference(ST_Transform(nzl.shape, 2193),bsl.shape)
        )
      );

    -- Update the changed suburbs
    UPDATE buildings_reference.suburb_locality bsl
    SET
      name = COALESCE(nzl.suburb_4th, nzl.suburb_3rd, nzl.suburb_2nd, nzl.suburb_1st),
      shape = ST_SetSRID(ST_Transform(nzl.shape, 2193), 2193)
    FROM
      admin_bdys.nz_locality nzl
    WHERE 
      bsl.external_suburb_locality_id = nzl.id
    AND (
      NOT ST_Equals(ST_SetSRID(ST_Transform(nzl.shape, 2193), 2193), bsl.shape)
      OR bsl.name != COALESCE(nzl.suburb_4th, nzl.suburb_3rd, nzl.suburb_2nd, nzl.suburb_1st)
    );

    -- Remove deleted suburbs
    DELETE FROM
      buildings_reference.suburb_locality
    WHERE 
      external_suburb_locality_id NOT IN (
        SELECT
          id
        FROM 
          admin_bdys.nz_locality
      );

    -- Updates building outlines where:
      -- It's external id is an 'old id'
      -- It Overlaps or is Within the difference polygon for the 'old id'
      -- It overlaps the difference polygon by the largest proportion
      -- The suburb with the most overlap is not the same as the old id
    UPDATE 
      buildings.building_outlines b
    SET 
      suburb_locality_id = buildings_reference.suburb_locality_intersect_polygon(b.shape),
      last_modified = NOW()
    FROM 
      changed_geometries cg
    WHERE 
      (ST_Within(b.shape, cg.shape) OR ST_Overlaps(b.shape, cg.shape))
      AND buildings_reference.suburb_locality_intersect_polygon(b.shape) != b.suburb_locality_id;

    DISCARD TEMP;

END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION buildings_reference.building_outlines_update_changed_and_deleted_suburb() IS
'Replace suburb values with the intersection result of buildings in the building_outlines table';


-- building_outlines_update_added_suburb (replace suburb values with the intersection result)
    -- params: 
    -- return: integer count of number of building outlines updated

CREATE OR REPLACE FUNCTION buildings_reference.building_outlines_update_added_suburb()
RETURNS void AS
$$
BEGIN
    -- add new suburbs to buildings_reference.suburb_locality
      -- (to get new suburb_locality_ids)
    CREATE TEMP TABLE added_suburbs (
    suburb_locality_id integer
    , external_suburb_locality_id integer
    , name character varying(60)
    , shape public.geometry(MultiPolygon, 2193)
  );

    WITH add_new_suburbs AS (
      INSERT INTO buildings_reference.suburb_locality (
      external_suburb_locality_id, name, shape
      )
      SELECT
      id,
      COALESCE(suburb_4th, suburb_3rd, suburb_2nd, suburb_1st),
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
    )

    INSERT INTO added_suburbs
    SELECT *
    FROM add_new_suburbs;

    -- update building outline suburb locality Id and last modified date where:
      -- the building is within/overlaps the new suburb
      -- The largest overlapping suburb has changed
    UPDATE 
      buildings.building_outlines b
    SET 
      suburb_locality_id = buildings_reference.suburb_locality_intersect_polygon(b.shape),
      last_modified = NOW()
    FROM 
      added_suburbs asb
    WHERE 
      (ST_Within(b.shape, asb.shape) OR ST_Overlaps(b.shape, asb.shape))
      AND buildings_reference.suburb_locality_intersect_polygon(b.shape) != b.suburb_locality_id;

    DISCARD TEMP;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION buildings_reference.building_outlines_update_added_suburb() IS
'Insert new suburb localities and replace old suburb values with the intersection result in the building_outlines table';

COMMIT;
