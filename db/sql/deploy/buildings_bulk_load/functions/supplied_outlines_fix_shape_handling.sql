-- Deploy nz-buildings:buildings_bulk_load/functions/supplied_outlines_fix_shape_handling to pg

BEGIN;

DROP FUNCTION IF EXISTS buildings_bulk_load.supplied_outlines_insert(integer, integer, geometry);

-- supplied_outlines_insert (Insert into buildings_bulk_load.supplied_outlines)
    -- params: integer supplied_dataset_id, integer external_outline_id, geometry shape
    -- return: integer supplied_outline_id

CREATE OR REPLACE FUNCTION buildings_bulk_load.supplied_outlines_insert(
      p_supplied_dataset_id integer
    , p_external_outline_id integer
    , p_shape geometry
)
RETURNS integer AS
$$

    INSERT INTO buildings_bulk_load.supplied_outlines(
          supplied_outline_id
        , supplied_dataset_id
        , external_outline_id
        , begin_lifespan
        , shape
    )
    VALUES (
          DEFAULT -- sequence
        , p_supplied_dataset_id
        , p_external_outline_id
        , now()
        , (ST_Dump(p_shape)).geom
    )
    RETURNING supplied_outline_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_bulk_load.supplied_outlines_insert(integer, integer, geometry) IS
'Insert new outlines into supplied outlines table';

COMMIT;
