-- Deploy nz-buildings:buildings_bulk_load/functions/existing_subset_extracts to pg

BEGIN;

-----------------------------------------------
-- buildings_bulk_load.existing_subset_extracts

-- Functions:

-- existing_subset_extracts_insert (insert into existing subset extracts table)
    -- params: integer building_outline_id, integer supplied_dataset_id, integer
            -- geometry shape
    -- return: count of rows inserted into table

-- existing_subset_extracts_remove_outline (remove existing outline from table as it has been deleted)
    -- params: integer[] building_outline_id
    -- return: intger number of outlines removed

-- existing_subset_extracts_update_supplied_dataset (update supplied dataset id of existing subset extracts outline)
    -- params: integer supplied_dataset_id, integer building_outline_id
    -- return: count of outlines added (should only be one)
-----------------------------------------------

-- Functions

-- existing_subset_extracts_insert (insert into existing subset extracts table)
    -- params: integer building_outline_id, integer supplied_dataset_id, integer
            -- geometry shape
    -- return: count of rows inserted into table

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

COMMENT ON FUNCTION buildings_bulk_load.existing_subset_extracts_insert(integer, integer, geometry) IS
'Insert outlines into existing subset extracts';

-- existing_subset_extracts_update_supplied_dataset (update supplied dataset id of existing subset extracts outline)
    -- params: integer supplied_dataset_id, integer building_outline_id
    -- return: count of outlines added (should only be one)

CREATE OR REPLACE FUNCTION buildings_bulk_load.existing_subset_extracts_update_supplied_dataset(
      p_supplied_dataset_id integer
    , p_building_outline_id integer
)
    RETURNS integer AS
$$
    WITH update_supplied_dataset AS (
        UPDATE buildings_bulk_load.existing_subset_extracts
        SET supplied_dataset_id = $1
        WHERE building_outline_id = $2
        RETURNING *
    )
    SELECT count(*)::integer FROM update_supplied_dataset;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_bulk_load.existing_subset_extracts_update_supplied_dataset(integer, integer) IS
'Update supplied_dataset_id in existing_subset_extracts table';

-- existing_subset_extracts_remove_outline (remove existing outline from table as it has been deleted)
    -- params: integer[] building_outline_id
    -- return: intger number of outlines removed

CREATE OR REPLACE FUNCTION buildings_bulk_load.existing_subset_extracts_remove_by_building_outline_id(integer[])
    RETURNS integer AS
$$

    WITH update_existing AS (
        DELETE FROM buildings_bulk_load.existing_subset_extracts
        WHERE building_outline_id = ANY($1)
        RETURNING *
    )
    SELECT count(*)::integer FROM update_existing;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_bulk_load.existing_subset_extracts_remove_by_building_outline_id(integer[]) IS
'Remove outline from existin subset extracts table';

COMMIT;
