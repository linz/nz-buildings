-------------------------------------------------------------------------
-- BULK LOAD OUTLINES insert into
-------------------------------------------------------------------------
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
        , p_suburb_locality_id --p_suburb_locality_id
        , p_town_city_id --p_town_city_id
        , p_territorial_authority_id --p_territorial_authority_id
        , now() --p_begin_lifespan
        , p_shape
    )
    RETURNING bulk_load_outline_id;

$$
LANGUAGE sql VOLATILE;

-------------------------------------------------------------------------
-- EXISTING SUBSET EXTRACT insert into
  -- returns number of rows inserted into table
-------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings_bulk_load.existing_subset_extracts_insert(
      p_building_outline_id integer
    , p_supplied_dataset_id integer
    , p_shape geometry
)
RETURNS integer AS
$$
    WITH insert_subset_extracts AS(
        INSERT INTO buildings_bulk_load.existing_subset_extracts(
              building_outline_id
            , supplied_dataset_id
            , shape
        )
        VALUES (
              p_building_outline_id
            , p_supplied_dataset_id
            , p_shape
        )
        RETURNING *
    )
    SELECT count(*)::integer FROM insert_subset_extracts

$$
LANGUAGE sql VOLATILE;

-------------------------------------------------------------------------
-- SUPPLIED DATASET insert into
-------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings_bulk_load.supplied_datasets_insert(
      p_description varchar(250)
    , p_supplier_id integer
)
RETURNS integer AS
$$

    INSERT INTO buildings_bulk_load.supplied_datasets(
          supplied_dataset_id
        , description
        , supplier_id
        , processed_date
        , transfer_date
    )
    VALUES (
          DEFAULT -- sequence
        , p_description
        , p_supplier_id
        , NULL --processed_date
        , NULL --transfer_date
    )
    RETURNING supplied_dataset_id;

$$
LANGUAGE sql VOLATILE;

-------------------------------------------------------------------------
-- ORGANISATION insert into
-------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings_bulk_load.organisation_insert(
      p_value varchar(250)
)
RETURNS integer AS
$$

    INSERT INTO buildings_bulk_load.organisation(
          organisation_id
        , value
    )
    VALUES (
          DEFAULT -- sequence
        , p_value

    )
    RETURNING organisation_id;

$$
LANGUAGE sql VOLATILE;