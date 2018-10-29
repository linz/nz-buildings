--------------------------------------------
-- buildings_common.capture_source_group
--------------------------------------------

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
