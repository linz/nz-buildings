-- Deploy nz-buildings:buildings_bulk_load/functions/related to pg

BEGIN;

--------------------------------------------
-- buildings_bulk_load.related

-- Functions:

-- building_outlines_related_select_by_dataset (select related building outlines by supplied_dataset)
    -- params: integer supplied_dataset_id
    -- return: integer[] building_outline_ids

-- building_related_select_by_dataset (select building ids by supplied_dataset_id)
    -- params: integer supplied_dataset_id
    -- return: integer[] building_ids

-- related_delete_existing_outlines (delete from related table by building_outline_id)
    -- params: integer building_outline_id
    -- return: integer building_outline_id removed

-- related_insert_building_outlines (insert new entry into related table)
    -- params: integer related_group_id, integer bulk_load_outline_id, integer qa_status_id
    -- return: integer related_id

-- related_group_insert (create new entry in related group insert table)
    -- params: None
    -- return: integer related_group_id

-- related_select_by_dataset (select bulk load ids in related table by supplied_datset)
    -- params: integer supplied_dataset_id
    -- return: integer[] distinct bulk_load_outline_ids

-- related_update_qa_status_id (update qa status of related outlines)
    -- params: integer qa_status_id, integer existing_id, integer bulk_load_outline_id
    -- return: count of outlines updated

--------------------------------------------

-- Functions

-- building_outlines_related_select_by_dataset (select related building outlines by supplied_dataset)
    -- params: integer supplied_dataset_id
    -- return: integer[] building_outline_ids

CREATE OR REPLACE FUNCTION buildings_bulk_load.building_outlines_related_select_by_dataset(integer)
RETURNS integer[] AS
$$

    SELECT ARRAY(
        SELECT related.building_outline_id
        FROM buildings_bulk_load.related
        WHERE related.bulk_load_outline_id = $1
    );

$$
LANGUAGE sql;

COMMENT ON FUNCTION buildings_bulk_load.building_outlines_related_select_by_dataset(integer) IS
'Select building_outline_id in related table';

-- building_related_select_by_dataset (select building ids by supplied_dataset_id)
    -- params: integer supplied_dataset_id
    -- return: integer[] building_ids

CREATE OR REPLACE FUNCTION buildings_bulk_load.buildings_related_select_by_dataset(integer)
RETURNS integer[] AS
$$

    SELECT ARRAY(
        SELECT outlines.building_id
        FROM buildings.building_outlines outlines
        JOIN buildings_bulk_load.related USING (building_outline_id)
        WHERE related.bulk_load_outline_id = $1
    );

$$
LANGUAGE sql;

COMMENT ON FUNCTION buildings_bulk_load.buildings_related_select_by_dataset(integer) IS
'Select building_id in related table';

-- related_delete_existing_outlines (delete from related table by building_outline_id)
    -- params: integer building_outline_id
    -- return: integer building_outline_id removed

CREATE OR REPLACE FUNCTION buildings_bulk_load.related_delete_existing_outlines(integer)
RETURNS integer AS
$$

    DELETE FROM buildings_bulk_load.related
    WHERE building_outline_id = $1
    RETURNING building_outline_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_bulk_load.related_delete_existing_outlines(integer) IS
'Delete from related table by building_outline_id';

-- related_insert_building_outlines (insert new entry into related table)
    -- params: integer related_group_id, integer bulk_load_outline_id, integer qa_status_id
    -- return: integer related_id

CREATE OR REPLACE FUNCTION buildings_bulk_load.related_insert_building_outlines(integer, integer, integer)
RETURNS integer AS
$$

    INSERT INTO buildings_bulk_load.related (related_group_id, bulk_load_outline_id, building_outline_id, qa_status_id)
    VALUES ($1, $2, $3, 2)
    RETURNING related.related_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_bulk_load.related_insert_building_outlines(integer, integer, integer) IS
'Insert new entry into related table';

-- related_group_insert (create new entry in related group insert table)
    -- params: None
    -- return: integer related_group_id

CREATE OR REPLACE FUNCTION buildings_bulk_load.related_group_insert()
RETURNS integer AS
$$

    INSERT INTO buildings_bulk_load.related_groups (related_group_id)
    VALUES (DEFAULT)
    RETURNING related_groups.related_group_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_bulk_load.related_group_insert() IS
'Create new entry in related group insert table';

-- related_select_by_dataset (select bulk load ids in related table by supplied_datset)
    -- params: integer supplied_dataset_id
    -- return: integer[] distinct bulk_load_outline_ids

CREATE OR REPLACE FUNCTION buildings_bulk_load.related_select_by_dataset(integer)
RETURNS integer[] AS
$$

    SELECT ARRAY(
        SELECT DISTINCT bulk_load_outline_id
        FROM buildings_bulk_load.related
        JOIN buildings_bulk_load.bulk_load_outlines supplied USING (bulk_load_outline_id)
        WHERE supplied.supplied_dataset_id = $1
        AND supplied.bulk_load_status_id != 3
        ORDER BY bulk_load_outline_id DESC
    );

$$
LANGUAGE sql;

COMMENT ON FUNCTION buildings_bulk_load.related_select_by_dataset(integer) IS
'Select bulk_load_outline_id in related table';

-- related_update_qa_status_id (update qa status of related outlines)
    -- params: integer qa_status_id, integer existing_id, integer bulk_load_outline_id
    -- return: count of outlines updated

CREATE OR REPLACE FUNCTION buildings_bulk_load.related_update_qa_status_id(integer, integer, integer)
RETURNS integer AS
$$

    WITH related_update AS (
        UPDATE buildings_bulk_load.related
        SET qa_status_id = $1
        WHERE related_group_id in(
            SELECT related_group_id
            FROM buildings_bulk_load.related
            WHERE building_outline_id = $2
            AND bulk_load_outline_id = $3
        )
        RETURNING *
    )
    SELECT count(*)::integer FROM related_update;

$$
LANGUAGE sql;

COMMENT ON FUNCTION buildings_bulk_load.related_update_qa_status_id(integer, integer, integer) IS
'Update qa status of related outlines';

COMMIT;
