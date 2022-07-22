#!/bin/sh

docker exec -u postgres db psql -a -f /nz-buildings/plugin/tests/testdata/db/buildings_reference.sql
docker exec -u postgres db psql -a -f /nz-buildings/plugin/tests/testdata/db/buildings_common.sql
docker exec -u postgres db psql -a -f /nz-buildings/plugin/tests/testdata/db/buildings.sql
docker exec -u postgres db psql -a -f /nz-buildings/plugin/tests/testdata/db/buildings_bulk_load.sql
docker exec -u postgres db psql -a -f /nz-buildings/plugin/tests/testdata/db/buildings_lds.sql
docker exec -u postgres db psql -a -f /nz-buildings/plugin/tests/testdata/db/update_sequences.sql
docker exec -u postgres db psql -c 'REFRESH MATERIALIZED VIEW buildings_reference.territorial_authority_grid;'
