-------------------------------------------------------------------------
-- CAPTURE SOURCE insert into
-------------------------------------------------------------------------
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

-------------------------------------------------------------------------
-- CAPTURE METHOD insert into
-------------------------------------------------------------------------
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

-------------------------------------------------------------------------
-- CAPTURE SOURCE GROUP insert into
-------------------------------------------------------------------------
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