-- Deploy buildings:buildings_common/functions/capture_source to pg

BEGIN;

--------------------------------------------
-- buildings_common.capture_source

-- Functions:
-- capture_source_insert (insert new capture source into table)
  -- params: integer capture_source_group_id, varchar(250) external_source_id
  -- return: integer capture_source_id
--------------------------------------------

-- Functions

-- capture_source_insert (insert new capture source into table)
  -- params: integer capture_source_group_id, varchar(250) external_source_id
  -- return: integer capture_source_id

CREATE OR REPLACE FUNCTION buildings_common.capture_source_insert(
      p_capture_source_group_id integer
    , p_external_source_id varchar(250)
)
RETURNS integer AS
$$

    INSERT INTO buildings_common.capture_source(
          capture_source_id
        , capture_source_group_id
        , external_source_id
    )
    VALUES (
          DEFAULT -- sequence
        , p_capture_source_group_id
        , p_external_source_id

    )
    RETURNING capture_source_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_common.capture_source_insert(integer, varchar(250)) IS
'Insert new capture source into table';

COMMIT;
