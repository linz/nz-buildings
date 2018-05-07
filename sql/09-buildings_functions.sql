-------------------------------------------------------------------
--BUILDING OUTLINES update end_lifespan
-------------------------------------------------------------------
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
'Update end_lifespan in BUILDING OUTLINES schema';

-------------------------------------------------------------------
--BUILDINGS update end_lifespan
-------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.buildings_update_end_lifespan(integer[])
    RETURNS integer AS
$$

    WITH update_buildings AS (
        UPDATE buildings.buildings
        SET end_lifespan = now()
        WHERE building_id = ANY($1)
        RETURNING *
    )
    SELECT count(*)::integer FROM update_buildings;

$$ LANGUAGE sql;

COMMENT ON FUNCTION buildings.buildings_update_end_lifespan(integer[]) IS
'Update end_lifespan in BUILDINGS schema';

-------------------------------------------------------------------
--BUILDING OUTLINES select from removed table
-------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings_bulk_load.building_outlines_removed_select_by_dataset(integer)
    RETURNS integer[] AS
$$

    SELECT ARRAY(
        SELECT removed.building_outline_id
        FROM buildings_bulk_load.removed
        JOIN buildings_bulk_load.existing_subset_extracts current USING (building_outline_id)
        WHERE current.supplied_dataset_id = $1
    )

$$ LANGUAGE sql;

COMMENT ON FUNCTION buildings_bulk_load.building_outlines_removed_select_by_dataset(integer) IS
'Select building_outline_id in removed table';
-------------------------------------------------------------------
--BUILDINGS select from removed table
-------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings_bulk_load.buildings_removed_select_by_dataset(integer)
    RETURNS integer[] AS
$$

    SELECT ARRAY(
        SELECT outlines.building_id
        FROM buildings.building_outlines outlines
        JOIN buildings_bulk_load.removed USING (building_outline_id)
        JOIN buildings_bulk_load.existing_subset_extracts current USING (building_outline_id)
        WHERE current.supplied_dataset_id = $1
    )

$$ LANGUAGE sql;

COMMENT ON FUNCTION buildings_bulk_load.buildings_removed_select_by_dataset(integer) IS
'Select building_id in removed table';



-------------------------------------------------------------------
--BUILDINGS create new records
-------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.fn_buildings_add_record()
    RETURNS integer AS
$$
            INSERT INTO buildings.buildings(building_id)
            VALUES ( DEFAULT )
            RETURNING building_id;

$$ LANGUAGE sql;


-------------------


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