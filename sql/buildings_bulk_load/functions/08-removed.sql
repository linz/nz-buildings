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
-- removed_insert_building_outlines (insert new building outline entry into table)
    -- params: integer building_outline_id
    -- return: building_outline_id inserted


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
CREATE OR REPLACE FUNCTION buildings_bulk_load.removed_delete_existing_outlines(integer)
RETURNS integer AS
$$

    DELETE FROM buildings_bulk_load.removed
    WHERE building_outline_id = $1
    RETURNING building_outline_id;

$$
LANGUAGE sql;

COMMENT ON FUNCTION buildings_bulk_load.buildings_removed_select_by_dataset(integer) IS
'Delete outline from removed table by building_outline_id';


-- removed_insert_building_outlines (insert new building outline entry into table)
    -- params: integer building_outline_id
    -- return: building_outline_id inserted
CREATE OR REPLACE FUNCTION buildings_bulk_load.removed_insert_bulk_load_outlines(integer)
RETURNS integer AS
$$

    INSERT INTO buildings_bulk_load.removed (building_outline_id, qa_status_id)
    VALUES ($1, 2)
    RETURNING removed.building_outline_id;

$$
LANGUAGE sql;

COMMENT ON FUNCTION buildings_bulk_load.removed_insert_bulk_load_outlines(integer) IS
'Insert new building_outline entry into removed table';
