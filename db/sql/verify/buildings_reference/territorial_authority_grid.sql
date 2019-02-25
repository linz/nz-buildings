-- Verify buildings:buildings_reference/territorial_authority_grid on pg

BEGIN;

SELECT
      territorial_authority_grid_id
    , territorial_authority_id
    , external_territorial_authority_id
    , name
    , shape
FROM buildings_reference.territorial_authority_grid
WHERE FALSE;

SELECT 1/count(*)
FROM pg_matviews
WHERE schemaname = 'buildings_reference'
AND matviewname = 'territorial_authority_grid';

ROLLBACK;
