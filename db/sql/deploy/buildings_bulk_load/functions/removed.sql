-- Deploy buildings:buildings_bulk_load/functions/removed to pg

BEGIN;

--------------------------------------------
-- buildings_bulk_load.removed

-- Function:

-- building_outlines_removed_select_by_dataset (select building outlines in removed by supplied dataset)
    -- params: integer supplied_dataset
    -- return: integer[] building_outline_ids

-- buildings_removed_select_by_dataset (select buildings in removed by supplied dataset)
    -- params: integer supplied_dataset_id
    -- return: integer[] building_ids

-- removed_delete_existing_outline (delete outline from removed table)
    -- params: integer building_outline_id
    -- return: building_outline_id removed

-- removed_delete_existing_outlines (delete from removed table mulitple outlines)
    -- params: integer[], building_outline_ids
    -- return: number of outlines updated

-- removed_insert_building_outlines (insert new building outline entry into table)
    -- params: integer building_outline_id
    -- return: building_outline_id inserted

-- removed_update_qa_status_id (update qa status of removed outlines)
    -- params: integer qa_status, integer building_outline_id
    -- return: count of outlines updated

--------------------------------------------

-- Functions

-- building_outlines_removed_select_by_dataset (select building outlines in removed by supplied dataset)
    -- params: integer supplied_dataset
    -- return: integer[] building_outline_ids

CREATE OR REPLACE FUNCTION buildings_bulk_load.building_outlines_removed_select_by_dataset(integer)
    RETURNS integer[] AS
$$

    SELECT ARRAY(
        SELECT removed.building_outline_id
        FROM buildings_bulk_load.removed
        JOIN buildings_bulk_load.existing_subset_extracts current USING (building_outline_id)
        WHERE current.supplied_dataset_id = $1
          AND removed.qa_status_id != 5
    )

$$ LANGUAGE sql;

COMMENT ON FUNCTION buildings_bulk_load.building_outlines_removed_select_by_dataset(integer) IS
'Select building_outline_id in removed table';


-- buildings_removed_select_by_dataset (select buildings in removed by supplied dataset)
    -- params: integer supplied_dataset_id
    -- return: integer[] building_ids

CREATE OR REPLACE FUNCTION buildings_bulk_load.buildings_removed_select_by_dataset(integer)
    RETURNS integer[] AS
$$

    SELECT ARRAY(
        SELECT outlines.building_id
        FROM buildings.building_outlines outlines
        JOIN buildings_bulk_load.removed USING (building_outline_id)
        JOIN buildings_bulk_load.existing_subset_extracts current USING (building_outline_id)
        WHERE current.supplied_dataset_id = $1
          AND removed.qa_status_id != 5
    )

$$ LANGUAGE sql;

COMMENT ON FUNCTION buildings_bulk_load.buildings_removed_select_by_dataset(integer) IS
'Select building_id in removed table';


-- removed_delete_existing_outline (delete outline from removed table)
    -- params: integer building_outline_id
    -- return: building_outline_id removed

CREATE OR REPLACE FUNCTION buildings_bulk_load.removed_delete_existing_outline(integer)
RETURNS integer AS
$$

    DELETE FROM buildings_bulk_load.removed
    WHERE building_outline_id = $1
    RETURNING building_outline_id;

$$
LANGUAGE sql;

COMMENT ON FUNCTION buildings_bulk_load.removed_delete_existing_outline(integer) IS
'Delete outline from removed table by building_outline_id';

-- removed_delete_existing_outlines (delete from removed table mulitple outlines)
    -- params: integer[], building_outline_ids
    -- return: number of outlines updated

CREATE OR REPLACE FUNCTION buildings_bulk_load.removed_delete_existing_outlines(integer[])
    RETURNS integer AS
$$

    WITH update_removed AS (
        DELETE FROM buildings_bulk_load.removed
        WHERE building_outline_id = ANY($1)
        RETURNING *
    )
    SELECT count(*)::integer FROM update_removed;

$$ LANGUAGE sql;

COMMENT ON FUNCTION buildings_bulk_load.removed_delete_existing_outlines(integer[]) IS
'remove list of outlines from removed table';

-- removed_insert_building_outlines (insert new building outline entry into table)
    -- params: integer building_outline_id
    -- return: building_outline_id inserted

CREATE OR REPLACE FUNCTION buildings_bulk_load.removed_insert_building_outlines(integer)
RETURNS integer AS
$$

    INSERT INTO buildings_bulk_load.removed (building_outline_id, qa_status_id)
    VALUES ($1, 2)
    RETURNING removed.building_outline_id;

$$
LANGUAGE sql;

COMMENT ON FUNCTION buildings_bulk_load.removed_insert_building_outlines(integer) IS
'Insert new building_outline entry into removed table';


-- removed_update_qa_status_id (update qa status of removed outlines)
    -- params: integer qa_status, integer building_outline_id
    -- return: count of outlines updated

CREATE OR REPLACE FUNCTION buildings_bulk_load.removed_update_qa_status_id(integer, integer)
    RETURNS integer AS
$$
    WITH removed_update AS (
        UPDATE buildings_bulk_load.removed
        SET qa_status_id = $1
        WHERE building_outline_id = $2
        RETURNING *
    )
    SELECT count(*)::integer FROM removed_update;

$$ LANGUAGE sql;

COMMENT ON FUNCTION buildings_bulk_load.removed_update_qa_status_id(integer, integer) IS
'Update qa status of removed outlines';

COMMIT;
