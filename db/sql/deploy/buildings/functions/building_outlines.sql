-- Deploy buildings:buildings/functions/building_outlines to pg

BEGIN;

--------------------------------------------
-- buildings.building_outlines

-- Functions:
-- building_outlines_insert (add new entry to building outlines table)
    -- params: integer building_id, integer capture_method_id, integer capture_source_id
            -- integer lifecycle_stage_id, integer suburb_locality_id, integer town_city_id
            -- integer territorial_authority_id, timestamp begin_lifespan, shape geometry
    -- return: new building_outline_id

-- building_outlines_insert_bulk (Create new added records in building outlines table)
    -- params: integer building_outline_id, integer bulk_load_outline_id
    -- return: building_outline_id

-- building_outlines_update_attributes (update the attributes of specified outline)
    -- params: integer building_outline_id, integer capture_method_id, integer lifecycle_stage_id,
            -- integer town_city_id, integer territorial_authority_id, timestamp begin_lifespan,
            -- shape geometry
    --return: number of outlines updated (should only be one)

-- building_outlines_update_capture_method (update capture method attribute)
    -- params integer building_outline_id, integer capture_method_id
    -- return: integer count number of outlines updated

-- building_outlines_update_end_lifespan (update the end lifespan attr of an outline)
    -- params: integer[]
    -- return: count of outlines updated

-- building outlines_update_shape (update the geometry of specified outline)
    -- params: shape to update to geometry, integer building_outline_id
    --return: number of outlines updated (should only be one)

--------------------------------------------

-- Functions

-- building_outlines_insert (add new entry to building outlines table)
    -- params: integer building_id, integer capture_method_id, integer capture_source_id
            -- integer lifecycle_stage_id, integer suburb_locality_id, integer town_city_id
            -- integer territorial_authority_id, timestamp begin_lifespan, shape geometry
    -- return: new building_outline_id

CREATE OR REPLACE FUNCTION buildings.building_outlines_insert(
      p_building_id integer
    , p_capture_method_id integer
    , p_capture_source_id integer
    , p_lifecycle_stage_id integer
    , p_suburb_locality_id integer
    , p_town_city_id integer
    , p_territorial_authority_id integer
    , p_begin_lifespan timestamp
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
        , town_city_id
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
        , p_town_city_id
        , p_territorial_authority_id
        , p_begin_lifespan
        , p_shape
    )
    RETURNING building_outline_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings.building_outlines_insert(integer, integer, integer, integer, integer, integer, integer, timestamp, geometry) IS
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
          , supplied.town_city_id
          , supplied.territorial_authority_id
          , supplied.begin_lifespan
          , supplied.shape
          )
        FROM buildings_bulk_load.bulk_load_outlines supplied
        WHERE supplied.bulk_load_outline_id = $2

$$ LANGUAGE sql;

COMMENT ON FUNCTION buildings.building_outlines_insert_bulk(integer, integer) IS
'Create new added records in building outlines table';


-- building_outlines_update_attributes (update the attributes of specified outline)
    -- params: integer building_outline_id, integer capture_method_id, integer lifecycle_stage_id,
            -- integer town_city_id, integer territorial_authority_id, timestamp begin_lifespan,
            -- shape geometry
    --return: number of outlines updated (should only be one)

CREATE OR REPLACE FUNCTION buildings.building_outlines_update_attributes(
      p_building_outline_id integer
    , p_capture_method_id integer
    , p_capture_source_id integer
    , p_lifecycle_stage_id integer
    , p_suburb_locality_id integer
    , p_town_city_id integer
    , p_territorial_authority_id integer
)
    RETURNS integer AS
$$
    WITH update_attributes AS (
        UPDATE buildings.building_outlines
        SET capture_method_id = $2
        , capture_source_id = $3
        , lifecycle_stage_id = $4
        , suburb_locality_id = $5
        , town_city_id = $6
        , territorial_authority_id = $7
        WHERE building_outline_id = $1
        RETURNING *
    )
    SELECT count(*)::integer FROM update_attributes;

$$ LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings.building_outlines_update_attributes(integer, integer, integer, integer, integer, integer, integer) IS
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

$$ LANGUAGE sql VOLATILE;

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

$$ LANGUAGE sql;

COMMENT ON FUNCTION buildings.building_outlines_update_end_lifespan(integer[]) IS
'Update end_lifespan in building outlines table';


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

$$ LANGUAGE sql;

COMMENT ON FUNCTION buildings.building_outlines_update_shape(geometry, integer) IS
'Update shape in building_outlines table';

COMMIT;
