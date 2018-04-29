-------------------------------------------------------------------------
-- BULK LOAD OUTLINES insert into
-------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings_bulk_load.fn_bulk_load_outlines_insert(
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
        , NULL --p_suburb_locality_id
        , NULL --p_town_city_id
        , NULL --p_territorial_authority_id
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
CREATE OR REPLACE FUNCTION buildings_bulk_load.fn_existing_subset_extract_insert(
      p_building_outline_id integer
    , p_supplied_dataset_id integer
    , p_shape geometry
)
RETURNS integer AS
$$

DECLARE
    v_rows_updated integer;

BEGIN

    INSERT INTO buildings_bulk_load.existing_subset_extract(
          building_outline_id
        , supplied_dataset_id
        , shape
    )
    VALUES (
          p_building_outline_id
        , p_supplied_dataset_id
        , p_shape
    );

    GET DIAGNOSTICS v_rows_updated = ROW_COUNT;

    RETURN v_rows_updated;
END;

$$
LANGUAGE plpgsql VOLATILE;

-------------------------------------------------------------------------
-- SUPPLIED DATASET insert into
-------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings_bulk_load.fn_supplied_datasets_insert(
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
CREATE OR REPLACE FUNCTION buildings_bulk_load.fn_organisation_insert(
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