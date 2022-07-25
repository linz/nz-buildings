#!/bin/sh

docker exec -u postgres db psql -a -f /nz-buildings/db/tests/testdata/plugin/buildings_reference.sql
docker exec -u postgres db psql -a -f /nz-buildings/db/tests/testdata/plugin/buildings_common.sql
docker exec -u postgres db psql -a -f /nz-buildings/db/tests/testdata/plugin/buildings.sql
docker exec -u postgres db psql -a -f /nz-buildings/db/tests/testdata/plugin/buildings_bulk_load.sql
docker exec -u postgres db psql -a -f /nz-buildings/db/tests/testdata/plugin/buildings_lds.sql
docker exec -u postgres db psql -a -f /nz-buildings/db/tests/testdata/plugin/update_sequences.sql
docker exec -u postgres db psql -c 'REFRESH MATERIALIZED VIEW buildings_reference.territorial_authority_grid;'
