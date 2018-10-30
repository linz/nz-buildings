--------------------------------------------
-- buildings_bulk_load.bulk_load_outlines

-- Functions:

-- bulk_load_outlines_insert (insert new bulk load outline)
    -- params: integer supplied_dataset_id, integer external_outline_id
            -- integer external_outline_id, integer bulk_load_status_id
            -- integer capture_method_id, integer suburb_locality_id
            -- integer town_city_id, integer territorial_authority_id,
            -- geometry shape
    -- return: integer new bulk_load_outline_id

-- bulk_load_outlines_insert_supplied (insert supplied outlines into bulk_load_outlines)
    -- params: integer supplied_dataset_id, integer bulk_load_status_id
            -- integer capture_method_id, integer capture_source_id
    -- return: integer count of supplied outlines added

-- bulk_load_outlines_remove_small_buildings (change bulk load status of buildings less than 10sqm)
    -- params: integer supplied_dataset_id
    -- return: number of small buildings that have been removed

-- bulk_load_outlines_update_attributes (update the attributes of an outlines)
    -- params: integer bulk_load_outline_id, integer bulk_load_status_id, integer
            -- capture_method_id, integer capture_source_id, integer suburb_locality_id
            -- integer town_city_id, integer territorial_authority_id, geometry shape
    -- return: count of number of outlines updated

-- bulk_load_outlines_update_capture_method (Update capture method in bulk_load_outlines table)
    -- params: integer bulk_load_outline_id, integer capture_method_id
    -- return: integer count of building outlines updated

-- bulk_load_outlines_update_shape (update the shape of an outline)
    -- params: geometry, integer bulk_load_outline_id
    -- return: number of outlines with updated shapes

--------------------------------------------

-- Functions

-- bulk_load_outlines_insert (insert new bulk load outline)
    -- params: integer supplied_dataset_id, integer external_outline_id
            -- integer external_outline_id, integer bulk_load_status_id
            -- integer capture_method_id, integer suburb_locality_id
            -- integer town_city_id, integer territorial_authority_id
            -- geometry shape
    -- return: integer new bulk_load_outline_id
CREATE OR REPLACE FUNCTION buildings_bulk_load.bulk_load_outlines_insert(
      p_supplied_dataset_id integer
    , p_external_outline_id integer
    , p_bulk_load_status_id integer
    , p_capture_method_id integer
    , p_capture_source_id integer
    , p_suburb_locality_id integer
    , p_town_city_id integer
    , p_territorial_authority_id integer
    , p_shape geometry
)
RETURNS integer AS
$$

    INSERT INTO buildings_bulk_load.bulk_load_outlines(
          bulk_load_outline_id
        , supplied_dataset_id
        , external_outline_id
        , bulk_load_status_id
        , capture_method_id
        , capture_source_id
        , suburb_locality_id
        , town_city_id
        , territorial_authority_id
        , begin_lifespan
        , shape
    )
    VALUES (
          DEFAULT -- sequence
        , p_supplied_dataset_id
        , p_external_outline_id
        , p_bulk_load_status_id
        , p_capture_method_id
        , p_capture_source_id
        , p_suburb_locality_id
        , p_town_city_id
        , p_territorial_authority_id
        , now()
        , p_shape
    )
    RETURNING bulk_load_outline_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_bulk_load.bulk_load_outlines_insert(integer, integer, integer, integer, integer, integer, integer, integer, geometry) IS
'Insert new bulk load outline';

-- bulk_load_outlines_insert_supplied (insert supplied outlines into bulk_load_outlines)
    -- params: integer supplied_dataset_id, integer bulk_load_status_id
            -- integer capture_method_id, integer capture_source_id
    -- return: integer count of supplied outlines added
CREATE OR REPLACE FUNCTION buildings_bulk_load.bulk_load_outlines_insert_supplied(
      p_supplied_dataset_id integer
    , p_bulk_load_status_id integer
    , p_capture_method_id integer
    , p_capture_source_id integer
)
RETURNS integer AS
$$

    WITH insert_supplied AS (
        INSERT INTO buildings_bulk_load.bulk_load_outlines(
              supplied_dataset_id
            , external_outline_id
            , bulk_load_status_id
            , capture_method_id
            , capture_source_id
            , suburb_locality_id
            , town_city_id
            , territorial_authority_id
            , begin_lifespan
            , shape
        )
        SELECT
              supplied_dataset_id
            , external_outline_id
            , p_bulk_load_status_id
            , p_capture_method_id
            , p_capture_source_id
            , buildings_reference.suburb_locality_intersect_polygon(shape)
            , buildings_reference.town_city_intersect_polygon(shape)
            , buildings_reference.territorial_authority_grid_intersect_polygon(shape)
            , now()
            , shape
        FROM buildings_bulk_load.supplied_outlines s
        WHERE s.supplied_dataset_id = p_supplied_dataset_id
        RETURNING *
    )
    SELECT count(*)::integer FROM insert_supplied;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_bulk_load.bulk_load_outlines_insert_supplied(integer, integer, integer, integer) IS
'Insert supplied outlines into bulk load outlines';


-- bulk_load_outlines_remove_small_buildings (change bulk load status of buildings less than 10sqm)
    -- params: integer supplied_dataset_id
    -- return: number of small buildings that have been removed
CREATE OR REPLACE FUNCTION buildings_bulk_load.bulk_load_outlines_remove_small_buildings(integer)
    RETURNS integer AS
$$
    WITH small_buildings AS (
        UPDATE buildings_bulk_load.bulk_load_outlines
        SET bulk_load_status_id = 3
        WHERE bulk_load_outline_id in (SELECT
            bulk_load_outline_id
        FROM buildings_bulk_load.bulk_load_outlines
        WHERE ST_Area(shape) < 10)
        AND supplied_dataset_id = $1
        RETURNING *
    )
    SELECT count(*)::integer FROM small_buildings;

$$ LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_bulk_load.bulk_load_outlines_remove_small_buildings(integer) IS
'Update bulk load status in bulk_load_outlines table of outlines less than 10sqm';


-- bulk_load_outlines_update_attributes (update the attributes of an outlines)
    -- params: integer bulk_load_outline_id, integer bulk_load_status_id, integer
            -- capture_method_id, integer capture_source_id, integer suburb_locality_id
            -- integer town_city_id, integer territorial_authority_id, geometry shape
    -- return: count of number of outlines updated
CREATE OR REPLACE FUNCTION buildings_bulk_load.bulk_load_outlines_update_attributes(
      p_bulk_load_outline_id integer
    , p_bulk_load_status_id integer
    , p_capture_method_id integer
    , p_capture_source_id integer
    , p_suburb_locality_id integer
    , p_town_city_id integer
    , p_territorial_authority_id integer
)
    RETURNS integer AS
$$
    WITH update_attributes AS (
        UPDATE buildings_bulk_load.bulk_load_outlines
        SET bulk_load_status_id = $2
        , capture_method_id = $3
        , capture_source_id = $4
        , suburb_locality_id = $5
        , town_city_id = $6
        , territorial_authority_id = $7
        WHERE bulk_load_outline_id = $1
        RETURNING *
    )
    SELECT count(*)::integer FROM update_attributes;

$$ LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_bulk_load.bulk_load_outlines_update_attributes(integer, integer, integer, integer, integer, integer, integer) IS
'Update attributes in bulk_load_outlines table';


-- bulk_load_outlines_update_capture_method (Update capture method in bulk_load_outlines table)
    -- params: integer bulk_load_outline_id, integer capture_method_id
    -- return: integer count of building outlines updated
CREATE OR REPLACE FUNCTION buildings_bulk_load.bulk_load_outlines_update_capture_method(
      p_bulk_load_outline_id integer
    , p_capture_method_id integer
)
    RETURNS integer AS
$$
    WITH update_capture_method AS(
        UPDATE buildings_bulk_load.bulk_load_outlines
        SET capture_method_id = $2
        WHERE bulk_load_outline_id = $1
        RETURNING *
    )
    SELECT count(*)::integer FROM update_capture_method;

$$ LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_bulk_load.bulk_load_outlines_update_capture_method(integer, integer) IS
'Update capture method in bulk_load_outlines table';


-- bulk_load_outlines_update_shape (update the shape of an outline)
    -- params: geometry, integer bulk_load_outline_id
    -- return: number of outlines with updated shapes
CREATE OR REPLACE FUNCTION buildings_bulk_load.bulk_load_outlines_update_shape(geometry, integer)
    RETURNS integer AS
$$
    WITH update_shape AS (
        UPDATE buildings_bulk_load.bulk_load_outlines
        SET shape = $1
        WHERE bulk_load_outline_id = $2
        RETURNING *
    )
    SELECT count(*)::integer FROM update_shape;

$$ LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_bulk_load.bulk_load_outlines_update_shape(geometry, integer) IS
'Update shape in bulk_load_outlines table';
