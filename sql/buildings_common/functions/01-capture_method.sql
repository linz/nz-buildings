--------------------------------------------
-- buildings_common.capture_method

-- Functions:
-- capture_method_insert (insert new entry into capture method table)
  -- params: varchar(250) value
  -- return: integer capture_method_id

--------------------------------------------

-- Functions

-- capture_method_insert (insert new entry into capture method table)
  -- params: varchar(250) value
  -- return: integer capture_method_id
CREATE OR REPLACE FUNCTION buildings_common.capture_method_insert(
      p_value varchar(250)
)
RETURNS integer AS
$$

    INSERT INTO buildings_common.capture_method(
          capture_method_id
        , value
    )
    VALUES (
          DEFAULT -- sequence
        , p_value

    )
    RETURNING capture_method_id;

$$
LANGUAGE sql VOLATILE;
