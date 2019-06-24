-- Deploy nz-buildings:buildings_reference/functions/protected_area_polygons to pg

BEGIN;

--------------------------------------------
-- buildings_reference.protected_areas

-- Functions

-- protected_areas_delete_by_external_id
    -- params: integer external_protected_areas_id
    -- return: integer protected_areas_id

-- protected_areas_insert
    -- params: integer external_protected_areas_id, varchar geometry
    -- return: integer protected_areas_id


--------------------------------------------

-- Functions

-- protected_areas_delete_by_external_id ()
    -- params: integer external_protected_areas_id
    -- return: integer protected_areas_id

CREATE OR REPLACE FUNCTION buildings_reference.protected_areas_delete_by_external_id(integer)
RETURNS integer AS
$$

    DELETE FROM buildings_reference.protected_areas
    WHERE external_protected_areas_id = $1
    RETURNING protected_areas_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.protected_areas_delete_by_external_id(integer) IS
'Delete from protected_areas table by external id';


-- protected_areas_insert
    -- params: integer external_protected_areas_id, varchar geometry
    -- return: integer protected_areas_id

CREATE OR REPLACE FUNCTION buildings_reference.protected_areas_insert(integer, varchar)
RETURNS integer AS
$$

    INSERT INTO buildings_reference.protected_areas (external_protected_areas_id, shape)
    VALUES ($1, ST_SetSRID(ST_GeometryFromText($2), 2193))
    RETURNING protected_areas_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.protected_areas_insert(integer, varchar) IS
'Insert new entry into protected_areas table';


-- protected_areas_update_shape_by_external_id
    -- params: integer external_protected_areas_id, varchar geometry
    -- return: integer protected_areas_id

CREATE OR REPLACE FUNCTION buildings_reference.protected_areas_update_shape_by_external_id(integer, varchar)
RETURNS integer AS
$$

    UPDATE buildings_reference.protected_areas
    SET shape = ST_SetSRID(ST_GeometryFromText($2), 2193)
    WHERE external_protected_areas_id = $1
    RETURNING protected_areas_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.protected_areas_update_shape_by_external_id(integer, varchar) IS
'Update geometry of protected areas based on external_protected_areas_id';

COMMIT;
