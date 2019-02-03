-- Deploy buildings:buildings_bulk_load/functions/deletion_description to pg

BEGIN;

--------------------------------------------
-- buildings_bulk_load.deletion_description

-- Functions:

-- delete_deleted_description (delete record from deletion description table)
    -- params: integer bulk_load_outline_id
    -- return: integer bulk_load_outline_id

-- deletion_description_insert (create new record in deletion description)
	-- params: integer bulk_load_outline_id varchar(250) description
	-- return: integer bulk_load_outline_id

--------------------------------------------

-- Functions

-- delete_deleted_description (delete record from deletion description table)
    -- params: integer bulk_load_outline_id
    -- return: integer bulk_load_outline_id

CREATE OR REPLACE FUNCTION buildings_bulk_load.delete_deleted_description(integer)
RETURNS integer AS
$$
    DELETE
    FROM buildings_bulk_load.deletion_description
    WHERE bulk_load_outline_id = $1
    RETURNING deletion_description.bulk_load_outline_id;

$$
LANGUAGE sql;

COMMENT ON FUNCTION buildings_bulk_load.delete_deleted_description(integer) IS
'Delete record from deletion description table';


-- deletion_description_insert (create new record in deletion description)
    -- params: integer bulk_load_outline_id varchar(250) description
    -- return: integer bulk_load_outline_id

CREATE OR REPLACE FUNCTION buildings_bulk_load.deletion_description_insert(integer, varchar(250))
RETURNS integer AS
$$

    INSERT INTO buildings_bulk_load.deletion_description (bulk_load_outline_id, description)
    VALUES ($1, $2)
    RETURNING deletion_description.bulk_load_outline_id;

$$
LANGUAGE sql;

COMMENT ON FUNCTION buildings_bulk_load.deletion_description_insert(integer, varchar(250)) IS
'Create new records in deletion description table';

COMMIT;
