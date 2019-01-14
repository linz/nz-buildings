--------------------------------------------
-- buildings_reference.reference_update_log

-- Functions

-- reference_update_log_insert
    -- params:
    -- return: integer update_id

-- reference_update_log_update_canal_boolean
    -- params: integer update_id
    -- return: integer update_id

-- reference_update_log_update_coastline_boolean
    -- params: integer update_id
    -- return: integer update_id

-- reference_update_log_update_lagoon_boolean
    -- params: integer update_id
    -- return: integer update_id

-- reference_update_log_update_lake_boolean
    -- params: integer update_id
    -- return: integer update_id

-- reference_update_log_update_pond_boolean
    -- params: integer update_id
    -- return: integer update_id

-- reference_update_log_update_rivers_boolean
    -- params: integer update_id
    -- return: integer update_id

-- reference_update_log_update_swamp_boolean
    -- params: integer update_id
    -- return: integer update_id

-- reference_update_log_update_suburb_locality_boolean
    -- params: integer update_id
    -- return: integer update_id

-- reference_update_log_update_town_city_boolean
    -- params: integer update_id
    -- return: integer update_id

-- reference_update_log_update_territorial_authority_boolean
    -- params: integer update_id
    -- return: integer update_id

-- reference_update_log_update_territorial_authority_grid_boolean
    -- params: integer update_id
    -- return: integer update_id

-- reference_update_log_update_capture_source_area_boolean
    -- params: integer update_id
    -- return: integer update_id

--------------------------------------------

-- Functions

-- reference_update_log_insert
    -- params:
    -- return: integer update_id

CREATE OR REPLACE FUNCTION buildings_reference.reference_update_log_insert()
RETURNS integer AS
$$
    INSERT INTO buildings_reference.reference_update_log(
        update_id
    )
    VALUES (
          DEFAULT -- sequence
    )
    RETURNING update_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.reference_update_log_insert() IS
'Insert new entry in reference_update_log table';


-- reference_update_log_update_canal_boolean
    -- params: integer update_id
    -- return: integer update_id

CREATE OR REPLACE FUNCTION buildings_reference.reference_update_log_update_canal_boolean(integer)
RETURNS integer AS
$$
    UPDATE buildings_reference.reference_update_log
    SET canals = True
    WHERE update_id = $1
    RETURNING update_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.reference_update_log_update_canal_boolean(integer) IS
'Update boolean values of reference log entry';

-- reference_update_log_update_coastline_boolean
    -- params: integer update_id
    -- return: integer update_id

CREATE OR REPLACE FUNCTION buildings_reference.reference_update_log_update_coastline_boolean(integer)
RETURNS integer AS
$$
    UPDATE buildings_reference.reference_update_log
    SET coastlines_and_islands = True
    WHERE update_id = $1
    RETURNING update_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.reference_update_log_update_coastline_boolean(integer) IS
'Update boolean values of reference log entry';


-- reference_update_log_update_lagoon_boolean
    -- params: integer update_id
    -- return: integer update_id

CREATE OR REPLACE FUNCTION buildings_reference.reference_update_log_update_lagoon_boolean(integer)
RETURNS integer AS
$$
    UPDATE buildings_reference.reference_update_log
    SET lagoons = True
    WHERE update_id = $1
    RETURNING update_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.reference_update_log_update_lagoon_boolean(integer) IS
'Update boolean values of reference log entry';


-- reference_update_log_update_lake_boolean
    -- params: integer update_id
    -- return: integer update_id

CREATE OR REPLACE FUNCTION buildings_reference.reference_update_log_update_lake_boolean(integer)
RETURNS integer AS
$$
    UPDATE buildings_reference.reference_update_log
    SET lakes = True
    WHERE update_id = $1
    RETURNING update_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.reference_update_log_update_lake_boolean(integer) IS
'Update boolean values of reference log entry';


-- reference_update_log_update_pond_boolean
    -- params: integer update_id
    -- return: integer update_id

CREATE OR REPLACE FUNCTION buildings_reference.reference_update_log_update_pond_boolean(integer)
RETURNS integer AS
$$
    UPDATE buildings_reference.reference_update_log
    SET ponds = True
    WHERE update_id = $1
    RETURNING update_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.reference_update_log_update_pond_boolean(integer) IS
'Update boolean values of reference log entry';


-- reference_update_log_update_rivers_boolean
    -- params: integer update_id
    -- return: integer update_id

CREATE OR REPLACE FUNCTION buildings_reference.reference_update_log_update_river_boolean(integer)
RETURNS integer AS
$$
    UPDATE buildings_reference.reference_update_log
    SET rivers = True
    WHERE update_id = $1
    RETURNING update_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.reference_update_log_update_river_boolean(integer) IS
'Update boolean values of reference log entry';


-- reference_update_log_update_swamp_boolean
    -- params: integer update_id
    -- return: integer update_id

CREATE OR REPLACE FUNCTION buildings_reference.reference_update_log_update_swamp_boolean(integer)
RETURNS integer AS
$$
    UPDATE buildings_reference.reference_update_log
    SET swamps = True
    WHERE update_id = $1
    RETURNING update_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.reference_update_log_update_swamp_boolean(integer) IS
'Update boolean values of reference log entry';


-- reference_update_log_update_suburb_locality_boolean
    -- params: integer update_id
    -- return: integer update_id

CREATE OR REPLACE FUNCTION buildings_reference.reference_update_log_update_suburb_locality_boolean(integer)
RETURNS integer AS
$$
    UPDATE buildings_reference.reference_update_log
    SET suburb_locality = True
    WHERE update_id = $1
    RETURNING update_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.reference_update_log_update_suburb_locality_boolean(integer) IS
'Update boolean values of reference log entry';


-- reference_update_log_update_town_city_boolean
    -- params: integer update_id
    -- return: integer update_id

CREATE OR REPLACE FUNCTION buildings_reference.reference_update_log_update_town_city_boolean(integer)
RETURNS integer AS
$$
    UPDATE buildings_reference.reference_update_log
    SET town_city = True
    WHERE update_id = $1
    RETURNING update_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.reference_update_log_update_town_city_boolean(integer) IS
'Update boolean values of reference log entry';


-- reference_update_log_update_territorial_authority_boolean
    -- params: integer update_id
    -- return: integer update_id

CREATE OR REPLACE FUNCTION buildings_reference.reference_update_log_update_territorial_authority_boolean(integer)
RETURNS integer AS
$$
    UPDATE buildings_reference.reference_update_log
    SET territorial_authority = True
    WHERE update_id = $1
    RETURNING update_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.reference_update_log_update_territorial_authority_boolean(integer) IS
'Update boolean values of reference log entry';


-- reference_update_log_update_territorial_authority_grid_boolean
    -- params: integer update_id
    -- return: integer update_id

CREATE OR REPLACE FUNCTION buildings_reference.reference_update_log_update_territorial_authority_grid_boolean(integer)
RETURNS integer AS
$$
    UPDATE buildings_reference.reference_update_log
    SET territorial_authority_grid = True
    WHERE update_id = $1
    RETURNING update_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.reference_update_log_update_territorial_authority_grid_boolean(integer) IS
'Update boolean values of reference log entry';


-- reference_update_log_update_capture_source_area_boolean
    -- params: integer update_id
    -- return: integer update_id

CREATE OR REPLACE FUNCTION buildings_reference.reference_update_log_update_capture_source_area_boolean(integer)
RETURNS integer AS
$$
    UPDATE buildings_reference.reference_update_log
    SET capture_source_area = True
    WHERE update_id = $1
    RETURNING update_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.reference_update_log_update_capture_source_area_boolean(integer) IS
'Update boolean values of reference log entry';
