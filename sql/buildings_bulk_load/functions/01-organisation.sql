--------------------------------------------
-- buildings_bulk_load.organisation

-- Functions:

-- organisation_insert (insert new value into organisation table)
  -- params: varchar(250) organisation
  -- return: new organisation_id
--------------------------------------------

-- Functions

-- organisation_insert (insert new value into organisation table)
  -- params: varchar(250) organisation
  -- return: new organisation_id
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

COMMENT ON FUNCTION buildings_bulk_load.organisation_insert(varchar(250)) IS
'Insert new entry in organisation table';
