#!/bin/sh

echo >&2 ""
echo >&2 "########################################"
echo >&2 "# Loading data into additional schemas #"
echo >&2 "########################################"
echo >&2 ""

echo >&2 "Loading create_test_admin_bdys_schema.sql"
docker exec -u postgres db psql -q -f /nz-buildings/db/tests/testdata/create_test_admin_bdys_schema.sql
echo >&2 "Loading admin_bdys.sql"
docker exec -u postgres db psql -q -f /nz-buildings/db/tests/testdata/db/admin_bdys.sql
echo >&2 "Loading create_test_aerial_schema.sql"
docker exec -u postgres db psql -q -f /nz-buildings/db/tests/testdata/create_test_aerial_schema.sql
echo >&2 "Loading aerial_lds.sql"
docker exec -u postgres db psql -q -f /nz-buildings/db/tests/testdata/db/aerial_lds.sql
