--------------------------------------------
-- buildings.lifecycle_stage

-- Functions:
-- lifecycle_stage_insert (insert new lifecycle_stage entry)
    -- param: p_value varchar(40)
    -- returns: new lifecycle_stage_id

--------------------------------------------

-- Functions

-- lifecycle_stage_insert (insert new lifecycle_stage entry)
    -- param: p_value varchar(40)
    -- returns: new lifecycle_stage_id
CREATE OR REPLACE FUNCTION buildings.lifecycle_stage_insert(
      p_value varchar(40)
)
RETURNS integer AS
$$

    INSERT INTO buildings.lifecycle_stage(
          lifecycle_stage_id
        , value
    )
    VALUES (
          DEFAULT -- sequence
        , p_value

    )
    RETURNING lifecycle_stage_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings.lifecycle_stage_insert(varchar(40)) IS
'Insert new lifecycle stage entry';
