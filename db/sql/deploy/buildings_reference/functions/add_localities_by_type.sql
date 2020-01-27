-- Deploy nz-buildings:buildings_reference/functions/add_localities_by_type to pg

BEGIN;

CREATE OR REPLACE FUNCTION buildings_reference.suburb_locality_insert_new_areas()
RETURNS integer[] AS
$$

    WITH insert_suburb AS (
        INSERT INTO buildings_reference.suburb_locality (
              external_suburb_locality_id
            , suburb_4th
            , suburb_3rd
            , suburb_2nd
            , suburb_1st
            , shape
        )
        SELECT
              id
            , suburb_4th
            , suburb_3rd
            , suburb_2nd
            , suburb_1st
            , ST_SetSRID(ST_Transform(shape, 2193), 2193)
        FROM admin_bdys.nz_locality
        WHERE type in ('ISLAND','LOCALITY','PARK_RESERVE','SUBURB')
        AND id NOT IN (
            SELECT external_suburb_locality_id
            FROM buildings_reference.suburb_locality
        )
        RETURNING *
    )
    SELECT ARRAY(
        SELECT suburb_locality_id
        FROM insert_suburb
    );

$$
LANGUAGE sql VOLATILE;

COMMIT;

