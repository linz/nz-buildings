--------------------------------------------
-- buildings_common.capture_source_group

-- capture_source_group_insert (insert new capture source group into table)
  -- params: varchar(80) value, varchar(400) description
  -- return: integer capture_source_group_id
--------------------------------------------

-- Functions

-- capture_source_group_insert (insert new capture source group into table)
  -- params: varchar(80) value, varchar(400) description
  -- return: integer capture_source_group_id
CREATE OR REPLACE FUNCTION buildings_common.capture_source_group_insert(
      p_value varchar(80)
    , p_description varchar(400)
)
RETURNS integer AS
$$

    INSERT INTO buildings_common.capture_source_group(
          capture_source_group_id
        , value
        , description
    )
    VALUES (
          DEFAULT -- sequence
        , p_value
        , p_description
    )
    RETURNING capture_source_group_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_common.capture_source_group_insert(varchar(80), varchar(400)) IS
'Insert new capture source group into table';
