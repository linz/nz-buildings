-- Deploy nz-buildings:buildings/functions/building_outlines to pg

BEGIN;

DROP FUNCTION buildings.building_outlines_insert(integer, integer, integer, integer, integer, integer, integer, geometry);

DROP FUNCTION buildings.building_outlines_update_attributes(integer, integer, integer, integer, integer, integer, integer);

DROP FUNCTION IF EXISTS buildings.building_outlines_update_town_city(integer[]);

--------------------------------------------
-- buildings.building_outlines

-- Functions:
-- building_outlines_insert (add new entry to building outlines table)
    -- params: integer building_id, integer capture_method_id, integer capture_source_id
            -- integer lifecycle_stage_id, integer suburb_locality_id
            -- integer territorial_authority_id, timestamp begin_lifespan, shape geometry
    -- return: new building_outline_id

-- building_outlines_insert_bulk (Create new added records in building outlines table)
    -- params: integer building_outline_id, integer bulk_load_outline_id
    -- return: building_outline_id

-- building_outlines_update_attributes (update the attributes of specified outline)
    -- params: integer building_outline_id, integer capture_method_id, integer lifecycle_stage_id,
            -- integer territorial_authority_id, timestamp begin_lifespan,
            -- shape geometry
    --return: number of outlines updated (should only be one)

-- building_outlines_update_capture_method (update capture method attribute)
    -- params integer building_outline_id, integer capture_method_id
    -- return: integer count number of outlines updated

-- building_outlines_update_end_lifespan (update the end lifespan attr of an outline)
    -- params: integer[]
    -- return: count of outlines updated

-- building_outlines_update_modified_date (update the modified date attr of building to now)
    -- params: integer, building_outline_id
    -- return: number of outlines updated

-- building_outlines_update_modified_date_by_building_id (update the modified date attr of building to now)
    -- params: integer, building_id
    -- return: number of outlines updated

-- building outlines_update_shape (update the geometry of specified outline)
    -- params: shape to update to geometry, integer building_outline_id
    --return: number of outlines updated (should only be one)

-- building_outlines_update_territorial_authority (Replace the TA values with the intersection result)
    -- params: integer[] list of territorial_authorities buildings must be within
    -- return: count(integer) number of outlines updated

--------------------------------------------

-- Functions

-- building_outlines_insert (add new entry to building outlines table)
    -- params: integer building_id, integer capture_method_id, integer capture_source_id
            -- integer lifecycle_stage_id, integer suburb_locality_id
            -- integer territorial_authority_id, timestamp begin_lifespan, shape geometry
    -- return: new building_outline_id

CREATE OR REPLACE FUNCTION buildings.building_outlines_insert(
      p_building_id integer
    , p_capture_method_id integer
    , p_capture_source_id integer
    , p_lifecycle_stage_id integer
    , p_suburb_locality_id integer
    , p_territorial_authority_id integer
    , p_shape geometry
)
RETURNS integer AS
$$

    INSERT INTO buildings.building_outlines(
          building_outline_id
        , building_id
        , capture_method_id
        , capture_source_id
        , lifecycle_stage_id
        , suburb_locality_id
        , territorial_authority_id
        , begin_lifespan
        , shape
    )
    VALUES (
          DEFAULT -- sequence
        , p_building_id
        , p_capture_method_id
        , p_capture_source_id
        , p_lifecycle_stage_id
        , p_suburb_locality_id
        , p_territorial_authority_id
        , DEFAULT
        , p_shape
    )
    RETURNING building_outline_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings.building_outlines_insert(integer, integer, integer, integer, integer, integer, geometry) IS
'Insert new building outline into table';


-- building_outlines_insert_bulk (Create new added records in building outlines table)
    -- params: integer building_outline_id, integer bulk_load_outline_id
    -- return: building_outline_id

CREATE OR REPLACE FUNCTION buildings.building_outlines_insert_bulk(integer, integer)
RETURNS integer AS
$$

    SELECT buildings.building_outlines_insert (
          $1
        , supplied.capture_method_id
        , supplied.capture_source_id
        , 1
        , supplied.suburb_locality_id
        , supplied.territorial_authority_id
        , supplied.shape
    )
    FROM buildings_bulk_load.bulk_load_outlines supplied
    WHERE supplied.bulk_load_outline_id = $2

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings.building_outlines_insert_bulk(integer, integer) IS
'Create new added records in building outlines table';


-- building_outlines_update_attributes (update the attributes of specified outline)
    -- params: integer building_outline_id, integer capture_method_id, integer lifecycle_stage_id,
            -- integer territorial_authority_id, timestamp begin_lifespan,
            -- shape geometry
    --return: number of outlines updated (should only be one)

CREATE OR REPLACE FUNCTION buildings.building_outlines_update_attributes(
      p_building_outline_id integer
    , p_capture_method_id integer
    , p_capture_source_id integer
    , p_lifecycle_stage_id integer
    , p_suburb_locality_id integer
    , p_territorial_authority_id integer
)
RETURNS integer AS
$$

    WITH update_attributes AS (
        UPDATE buildings.building_outlines
        SET
              capture_method_id = $2
            , capture_source_id = $3
            , lifecycle_stage_id = $4
            , suburb_locality_id = $5
            , territorial_authority_id = $6
        WHERE building_outline_id = $1
        RETURNING *
    )
    SELECT count(*)::integer FROM update_attributes;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings.building_outlines_update_attributes(integer, integer, integer, integer, integer, integer) IS
'Update attributes in building_outlines table';


-- building_outlines_update_capture_method (update capture method attribute)
    -- params integer building_outline_id, integer capture_method_id
    -- return: integer count number of outlines updated

CREATE OR REPLACE FUNCTION buildings.building_outlines_update_capture_method(
      p_building_outline_id integer
    , p_capture_method_id integer
)
RETURNS integer AS
$$

    WITH update_capture_method AS(
        UPDATE buildings.building_outlines
        SET capture_method_id = $2
        WHERE building_outline_id = $1
        RETURNING *
    )
    SELECT count(*)::integer FROM update_capture_method;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings.building_outlines_update_capture_method(integer, integer) IS
'Update capture method in building_outlines table';


-- building_outlines_update_end_lifespan (update the end lifespan attr of an outline)
    -- params: integer[]
    -- return: count of outlines updated

CREATE OR REPLACE FUNCTION buildings.building_outlines_update_end_lifespan(integer[])
RETURNS integer AS
$$

    WITH update_building_outlines AS (
        UPDATE buildings.building_outlines
        SET end_lifespan = now()
        WHERE building_outline_id = ANY($1)
        RETURNING *
    )
    SELECT count(*)::integer FROM update_building_outlines;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings.building_outlines_update_end_lifespan(integer[]) IS
'Update end_lifespan in building outlines table';

-- building_outlines_update_modified_date (update the modified date attr of building to now)
    -- params: integer, building_outline_id
    -- return: number of outlines updated

CREATE OR REPLACE FUNCTION buildings.building_outlines_update_modified_date(integer)
    RETURNS integer AS
$$
    WITH update_buildings AS (
        UPDATE buildings.building_outlines
        SET last_modified = now()
        WHERE building_outline_id = $1
        RETURNING *
    )
    SELECT count(*)::integer FROM update_buildings;

$$ LANGUAGE sql;

COMMENT ON FUNCTION buildings.building_outlines_update_modified_date(integer) IS
'Update modified_date of outline in building_outlines table';


-- building_outlines_update_modified_date_by_building_id (update the modified date attr of building to now)
    -- params: integer, building_id
    -- return: number of outlines updated

CREATE OR REPLACE FUNCTION buildings.building_outlines_update_modified_date_by_building_id(integer)
    RETURNS integer AS
$$
    WITH update_buildings AS (
        UPDATE buildings.building_outlines
        SET last_modified = now()
        WHERE building_outline_id in (
            SELECT building_outline_id
            FROM buildings.building_outlines
            WHERE building_id = $1
            AND end_lifespan is NULL
        )
        RETURNING *
    )
    SELECT count(*)::integer FROM update_buildings;

$$ LANGUAGE sql;

COMMENT ON FUNCTION buildings.building_outlines_update_modified_date_by_building_id(integer) IS
'Update modified_date of outline in building_outlines table by building_id';

-- building outlines_update_shape (update the geometry of specified outline)
    -- params: shape to update to geometry, integer building_outline_id
    -- return: number of outlines updated (should only be one)

CREATE OR REPLACE FUNCTION buildings.building_outlines_update_shape(geometry, integer)
RETURNS integer AS
$$

    WITH update_buildings AS (
        UPDATE buildings.building_outlines
        SET shape = $1
        WHERE building_outline_id = $2
        RETURNING *
    )
    SELECT count(*)::integer FROM update_buildings;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings.building_outlines_update_shape(geometry, integer) IS
'Update shape in building_outlines table';

-- building_outlines_update_territorial_authority (Replace the TA values with the intersection result)
    -- params: integer[] list of territorial_authorities buildings must be within
    -- return: count(integer) number of outlines updated

CREATE OR REPLACE FUNCTION buildings.building_outlines_update_territorial_authority(integer[])
RETURNS integer AS
$$

    WITH update_territorial_auth AS (
        UPDATE buildings.building_outlines outlines
        SET territorial_authority_id = territorial_authority_intersect.territorial_authority_intersect_polygon
        FROM (
            SELECT
                  buildings_reference.territorial_authority_intersect_polygon(outlines.shape)
                , outlines.building_outline_id
            FROM buildings.building_outlines outlines
        ) territorial_authority_intersect
        WHERE outlines.building_outline_id = territorial_authority_intersect.building_outline_id
        AND territorial_authority_id = ANY($1)
        RETURNING *
    )
    SELECT count(*)::integer FROM update_territorial_auth;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings.building_outlines_update_territorial_authority(integer[]) IS
'Replace the TA values with the intersection result for all buildings in building_outlines';

COMMIT;
