#!/bin/sh

echo >&2 ""
echo >&2 "##################################"
echo >&2 "# Loading QGIS testing test data #"
echo >&2 "##################################"
echo >&2 ""

echo >&2 "Loading buildings_reference.sql"
docker exec -u postgres db psql -q -f /nz-buildings/db/tests/testdata/plugin/buildings_reference.sql
echo >&2 "Loading buildings_common.sql"
docker exec -u postgres db psql -q -f /nz-buildings/db/tests/testdata/plugin/buildings_common.sql
echo >&2 "Loading buildings.sql"
docker exec -u postgres db psql -q -f /nz-buildings/db/tests/testdata/plugin/buildings.sql
echo >&2 "Loading buildings_bulk_load.sql"
docker exec -u postgres db psql -q -f /nz-buildings/db/tests/testdata/plugin/buildings_bulk_load.sql
echo >&2 "Loading buildings_lds.sql"
docker exec -u postgres db psql -q -f /nz-buildings/db/tests/testdata/plugin/buildings_lds.sql
echo >&2 "Loading update_sequences.sql"
docker exec -u postgres db psql -q -f /nz-buildings/db/tests/testdata/plugin/update_sequences.sql
echo >&2 "Refreshing buildings_reference.territorial_authority_grid materialized view"
docker exec -u postgres db psql -q -c 'REFRESH MATERIALIZED VIEW buildings_reference.territorial_authority_grid;'
