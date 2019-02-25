-- Revert buildings:buildings_reference/territorial_authority_grid from pg

BEGIN;

CREATE TEMP TABLE ta_grid_data (
      territorial_authority_grid_id integer
    , territorial_authority_id integer
    , external_territorial_authority_id integer
    , name character varying(100)
    , shape public.geometry(MultiPolygon, 2193)
);

INSERT INTO ta_grid_data
SELECT *
FROM buildings_reference.territorial_authority_grid;

DROP MATERIALIZED VIEW buildings_reference.territorial_authority_grid CASCADE;

-- Territorial Authority Grid
-- For faster spatial operations
CREATE TABLE buildings_reference.territorial_authority_grid (
      territorial_authority_grid_id serial PRIMARY KEY
    , territorial_authority_id integer REFERENCES buildings_reference.territorial_authority (territorial_authority_id)
    , external_territorial_authority_id integer
    , name character varying(100)
    , shape public.geometry(MultiPolygon, 2193)
);

CREATE INDEX shx_territorial_authority_grid
    ON buildings_reference.territorial_authority_grid USING gist (shape);

COMMENT ON TABLE buildings_reference.territorial_authority_grid IS
'territorial_authority modified into grid to allow for faster spatial operations';

COMMENT ON COLUMN buildings_reference.territorial_authority_grid.territorial_authority_grid_id IS
'Unique identifier for the territorial_authority_grid.';
COMMENT ON COLUMN buildings_reference.territorial_authority_grid.territorial_authority_id IS
'The territorial_authority_id of the grid.';
COMMENT ON COLUMN buildings_reference.territorial_authority_grid.external_territorial_authority_id IS
'The external_territorial_authority_id of the grid.';
COMMENT ON COLUMN buildings_reference.territorial_authority_grid.name IS
'The name of the territorial authority of the grid.';

INSERT INTO buildings_reference.territorial_authority_grid
SELECT *
FROM ta_grid_data;

DISCARD TEMP;

COMMIT;
