--------------------------------------------
-- buildings_reference.capture_source_area

-- Functions

-- capture_source_area_insert (insert new capture source area)
    -- params: p_external_area_polygon_id varchar(250)
            -- p_area_title varchar(250)
            -- p_shape geometry
    -- return: integer area_polygon_id
--------------------------------------------

-- Functions

-- capture_source_area_insert (insert new capture source area)
    -- params: p_external_area_polygon_id varchar(250)
            -- p_area_title varchar(250)
            -- p_shape geometry
    -- return: integer area_polygon_id
CREATE OR REPLACE FUNCTION buildings_reference.capture_source_area_insert(
      p_external_area_polygon_id varchar(250)
    , p_area_title varchar(250)
    , p_shape geometry
)
RETURNS integer AS
$$

    INSERT INTO buildings_reference.capture_source_area(
          area_polygon_id
        , external_area_polygon_id
        , area_title
        , shape
    )
    VALUES (
          DEFAULT
        , p_external_area_polygon_id
        , p_area_title
        , p_shape
    )
    RETURNING area_polygon_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.capture_source_area_insert(varchar(250), varchar(250), geometry) IS
'Insert new capture source area';
