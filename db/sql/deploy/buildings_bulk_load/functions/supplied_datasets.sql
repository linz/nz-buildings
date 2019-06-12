-- Deploy nz-buildings:buildings_bulk_load/functions/supplied_datasets to pg

BEGIN;

--------------------------------------------
-- buildings_bulk_load.supplied_datasets

-- Functions:
-- supplied_datasets_insert (insert new supplied dataset)
    -- params: varchar(250) description, integer supplier_id
    -- return: new supplied_dataset_id

-- supplied_datasets_select_transfer_date (get transfer date of supplied dataset)
    -- params: integer supplied_dataset
    -- return: timestamp transfer_date

-- supplied_datasets_update_processed_date (update processed date of supplied dataset)
    -- params: integer supplied_dataset_id
    -- return: integer count of datasets updated (should only be one)

-- supplied_datasets_update_transfer_date (update transfer date of supplied dataset)
    -- params: integer supplied_datset_id
    -- return: integer, count of datasets updated (should only be one)

--------------------------------------------

-- Functions

-- supplied_datasets_insert (insert new supplied dataset)
    -- params: varchar(250) description, integer supplier_id
    -- return: new supplied_dataset_id

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

COMMENT ON FUNCTION buildings_bulk_load.supplied_datasets_insert(varchar(250), integer) IS
'Insert new supplied dataset';


-- supplied_datasets_select_transfer_date (get transfer date of supplied dataset)
    -- params: integer supplied_dataset
    -- return: timestamp transfer_date

CREATE OR REPLACE FUNCTION buildings_bulk_load.supplied_datasets_select_transfer_date(integer)
RETURNS timestamp AS
$$

    SELECT transfer_date
    FROM buildings_bulk_load.supplied_datasets
    WHERE buildings_bulk_load.supplied_datasets.supplied_dataset_id = $1

$$
LANGUAGE sql;

COMMENT ON FUNCTION buildings_bulk_load.supplied_datasets_select_transfer_date(integer) IS
'Return transfer_date in supplied_datasets table';


-- supplied_datasets_update_processed_date (update processed date of supplied dataset)
    -- params: integer supplied_dataset_id
    -- return: integer count of datasets updated (should only be one)

CREATE OR REPLACE FUNCTION buildings_bulk_load.supplied_datasets_update_processed_date(integer)
RETURNS integer AS
$$

    WITH update_processed_date AS (
        UPDATE buildings_bulk_load.supplied_datasets
        SET processed_date = now()
        WHERE supplied_dataset_id = $1
        RETURNING *
    )
    SELECT count(*)::integer FROM update_processed_date;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_bulk_load.supplied_datasets_update_processed_date(integer) IS
'Update processed_date in supplied_datasets table';


-- supplied_datasets_update_transfer_date (update transfer date of supplied dataset)
    -- params: integer supplied_datset_id
    -- return: integer, count of datasets updated (should only be one)

CREATE OR REPLACE FUNCTION buildings_bulk_load.supplied_datasets_update_transfer_date(integer)
RETURNS integer AS
$$
    WITH update_transfer_date AS (
        UPDATE buildings_bulk_load.supplied_datasets
        SET transfer_date = now()
        WHERE supplied_dataset_id = $1
        RETURNING *
    )
    SELECT count(*)::integer FROM update_transfer_date;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_bulk_load.supplied_datasets_update_transfer_date(integer) IS
'Update transfer_date in supplied_datasets table';


COMMIT;
