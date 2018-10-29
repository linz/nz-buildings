--------------------------------------------
-- buildings_bulk_load.deletion_description

-- Functions:
-- deletion_description_insert (create new record in deletion description)
	-- params: integer bulk_load_outline_id varchar(250) description
	-- return: integer bulk_load_outline_id

--------------------------------------------

-- Functions


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
