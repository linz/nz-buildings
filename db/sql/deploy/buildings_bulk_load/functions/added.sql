-- Deploy nz-buildings:buildings_bulk_load/functions/added to pg

BEGIN;

--------------------------------------------
-- buildings_bulk_load.added

-- Functions:

-- added_delete_bulk_load_outline (delete from added by bulk_load_outline_id)
    -- params: integer bulk_load_outline_id
    -- return: bulk_load_outline_id that was deleted

-- added_insert_bulk_load_outlines (insert bulk load outline into added table)
    -- params: integer bulk_load_outline_id, integer qa_status_id
    -- return: bulk_load_outline_id added

-- added_select_by_dataset (select from added by dataset)
    -- params: integer
    -- return: integer[] bulk_load_outline_id

--------------------------------------------

-- Functions

-- added_delete_bulk_load_outline (delete from added by bulk_load_outline_id)
    -- params: integer bulk_load_outline_id
    -- return: bulk_load_outline_id that was deleted

CREATE OR REPLACE FUNCTION buildings_bulk_load.added_delete_bulk_load_outlines(integer)
RETURNS integer AS
$$

    DELETE FROM buildings_bulk_load.added
    WHERE bulk_load_outline_id = $1
    RETURNING bulk_load_outline_id;

$$
LANGUAGE sql;

COMMENT ON FUNCTION buildings_bulk_load.added_delete_bulk_load_outlines(integer) IS
'Delete outline from added table by bulk_load_outline_id';


-- added_insert_all_bulk_loaded_outlines (Insert all new outlines to into added table)
    -- params: integer supplied_dataset_id
    -- return: number of outlines added to added table

CREATE OR REPLACE FUNCTION buildings_bulk_load.added_insert_all_bulk_loaded_outlines(integer)
RETURNS integer AS
$$
    
    WITH add_bulk AS (
        INSERT INTO buildings_bulk_load.added (bulk_load_outline_id, qa_status_id)
        SELECT blo.bulk_load_outline_id, 1
        FROM buildings_bulk_load.bulk_load_outlines blo
        WHERE blo.bulk_load_status_id !=3
        AND blo.supplied_dataset_id = $1
        RETURNING *
    )
    SELECT count(*)::integer FROM add_bulk;

$$
LANGUAGE sql;

COMMENT ON FUNCTION buildings_bulk_load.added_insert_all_bulk_loaded_outlines(integer) IS
'Insert all new outlines to into added table';

-- added_insert_bulk_load_outlines (insert bulk load outline into added table)
    -- params: integer bulk_load_outline_id, integer qa_status_id
    -- return: bulk_load_outline_id added

CREATE OR REPLACE FUNCTION buildings_bulk_load.added_insert_bulk_load_outlines(integer, integer)
RETURNS integer AS
$$

    INSERT INTO buildings_bulk_load.added (bulk_load_outline_id, qa_status_id)
    VALUES ($1, $2)
    RETURNING added.bulk_load_outline_id;

$$
LANGUAGE sql;

COMMENT ON FUNCTION buildings_bulk_load.added_insert_bulk_load_outlines(integer, integer) IS
'Insert bulk load outline into added table';

-- added_select_by_dataset (select from added by dataset)
    -- params: integer
    -- return: integer[] bulk_load_outline_id

CREATE OR REPLACE FUNCTION buildings_bulk_load.added_select_by_dataset(integer)
RETURNS integer[] AS
$$

    SELECT ARRAY(
        SELECT bulk_load_outline_id
        FROM buildings_bulk_load.added
        JOIN buildings_bulk_load.bulk_load_outlines supplied USING (bulk_load_outline_id)
        WHERE supplied.supplied_dataset_id = $1
        AND supplied.bulk_load_status_id != 3
    );

$$ LANGUAGE sql;

COMMENT ON FUNCTION buildings_bulk_load.added_select_by_dataset(integer) IS
'Select bulk_load_outline_id in added table';

COMMIT;
