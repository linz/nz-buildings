-------------------------------------------------------------------
--BUILDINGS insert into
-------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.fn_buildings_insert()
RETURNS integer AS
$$

    INSERT INTO buildings.buildings(
          building_id
        , begin_lifespan
    )
    VALUES (
          DEFAULT -- sequence
        , DEFAULT -- now()
    )
    RETURNING building_id;

$$
LANGUAGE sql VOLATILE;

----------------------------------------------------------------
-- BUILDING OUTLINES insert into
----------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.fn_building_outlines_insert(
      p_building_id integer
    , p_capture_method_id integer
    , p_capture_source_id integer
    , p_lifecycle_stage_id integer
    , p_suburb_locality_id integer
    , p_town_city_id integer
    , p_territorial_authority_id integer
    , p_begin_lifespan timestamptz
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

-------------------------------------------------------------------------
-- LIFECYCLE STAGE insert into
-------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.fn_lifecycle_stage_insert(
      p_value varchar(40)
)
RETURNS integer AS
$$

    INSERT INTO buildings.lifecycle_stage(
          lifecycle_stage_id
        , value
    )
    VALUES (
          DEFAULT -- sequence
        , p_value

    )
    RETURNING lifecycle_stage_id;

$$
LANGUAGE sql VOLATILE;