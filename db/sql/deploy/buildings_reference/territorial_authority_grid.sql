-- Deploy buildings:buildings_reference/territorial_authority_grid to pg

BEGIN;

DROP TABLE buildings_reference.territorial_authority_grid CASCADE;

-- Territorial Authority Grid
-- For faster spatial operations
CREATE MATERIALIZED VIEW buildings_reference.territorial_authority_grid AS
-- Get extent of TA table and x and y grid number counts
WITH nz_extent AS (
    SELECT
          ST_SetSRID(CAST(ST_Extent(shape) AS geometry), 2193) AS geom_extent
        , 300 AS x_grid_count
        , 250 AS y_grid_count
    FROM buildings_reference.territorial_authority
),
-- Get grid dimensions: x and y lengths and overall extent
grid_dim AS (
    SELECT
          (ST_XMax(geom_extent) - ST_XMin(geom_extent)) / x_grid_count AS g_width
        , ST_XMin(geom_extent) AS xmin
        , ST_XMax(geom_extent) AS xmax
        , (ST_YMax(geom_extent) - ST_YMin(geom_extent)) / y_grid_count AS g_height
        , ST_YMin(geom_extent) AS ymin
        , ST_YMax(geom_extent) AS ymax
    FROM nz_extent
),
-- Divide TA extent into grid
grid AS (
    SELECT ST_MakeEnvelope(
          xmin + (x - 1) * g_width
        , ymin + (y - 1) * g_height
        , xmin + x * g_width
        , ymin + y * g_height
        , 2193
    ) AS grid_geom
    FROM (
        SELECT generate_series(1, x_grid_count)
        FROM nz_extent
    ) AS x(x)
    CROSS JOIN (
        SELECT generate_series(1, y_grid_count)
        FROM nz_extent
    ) AS y(y)
    CROSS JOIN grid_dim
)
-- Select TA attributes and cut grid by TA boundaries
SELECT
      row_number() OVER(ORDER BY territorial_authority_id DESC) AS territorial_authority_grid_id
    , territorial_authority_id
    , external_territorial_authority_id
    , name
    , ST_Intersection(ta.shape, g.grid_geom) AS shape
FROM buildings_reference.territorial_authority ta
JOIN grid g ON ST_Intersects(ta.shape, g.grid_geom);

CREATE INDEX shx_territorial_authority_grid
    ON buildings_reference.territorial_authority_grid USING gist (shape);

COMMENT ON MATERIALIZED VIEW buildings_reference.territorial_authority_grid IS
'Territorial_authority modified into grid to allow for faster spatial operations';

COMMENT ON COLUMN buildings_reference.territorial_authority_grid.territorial_authority_grid_id IS
'Unique identifier for the territorial_authority_grid.';
COMMENT ON COLUMN buildings_reference.territorial_authority_grid.territorial_authority_id IS
'The territorial_authority_id of the grid.';
COMMENT ON COLUMN buildings_reference.territorial_authority_grid.external_territorial_authority_id IS
'The external_territorial_authority_id of the grid.';
COMMENT ON COLUMN buildings_reference.territorial_authority_grid.name IS
'The name of the territorial authority of the grid.';

COMMIT;
