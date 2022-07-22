#!/bin/sh

docker exec -u postgres db psql -a -f /nz-buildings/db/tests/testdata/create_test_admin_bdys_schema.sql
docker exec -u postgres db psql -a -f /nz-buildings/db/tests/testdata/db/admin_bdys.sql
docker exec -u postgres db psql -a -f /nz-buildings/db/tests/testdata/create_test_aerial_schema.sql
docker exec -u postgres db psql -a -f /nz-buildings/db/tests/testdata/db/aerial_lds.sql
