#!/bin/bash

export SCRIPTSDIR=/usr/share/nz-buildings/
export DATADIR=$HOME/dev/nz-buildings

pg_dump --column-inserts --data-only --schema=admin_bdys nz-buildings-pgtap-db > ${DATADIR}/db/tests/testdata/db/admin_bdys.sql
pg_dump --column-inserts --data-only --schema=aerial_lds nz-buildings-pgtap-db > ${DATADIR}/db/tests/testdata/db/aerial_lds.sql
pg_dump --column-inserts --data-only --schema=buildings nz-buildings-pgtap-db > ${DATADIR}/db/tests/testdata/db/buildings.sql
pg_dump --column-inserts --data-only --schema=buildings_common nz-buildings-pgtap-db > ${DATADIR}/db/tests/testdata/db/buildings_common.sql
pg_dump --column-inserts --data-only --schema=buildings_bulk_load nz-buildings-pgtap-db > ${DATADIR}/db/tests/testdata/db/buildings_bulk_load.sql
pg_dump --column-inserts --data-only --schema=buildings_reference nz-buildings-pgtap-db > ${DATADIR}/db/tests/testdata/db/buildings_reference.sql
pg_dump --column-inserts --data-only --schema=buildings_lds nz-buildings-pgtap-db > ${DATADIR}/db/tests/testdata/db/buildings_lds.sql

for file in ${DATADIR}/db/tests/testdata/db/*.sql; do
    echo ${file} >&2
    sed -i '/^SET/ d' ${file}
    sed -i '/^SELECT/ d' ${file}
    sed -i '/dump/ Id' ${file}
    sed -i '/--$/ d' ${file}
    sed -i '/--/ {/TABLE DATA/! d}' ${file}
    sed -i '/^$/ d' ${file}
    sed -i '/^--/ i \\' ${file}
    sed -i '/^--/ a \\' ${file}

    while read line; do
        if [[ $line == *"--"* ]]; then
            table_name=${line##*Data for Name: }
            table_name=${table_name%%; Type*}
            schema_name=${line##*Schema: }
            schema_name=${schema_name%%; Owner*}
            table_name="-- $schema_name.$table_name"
            sed -i 's/'"${line}"'/'"${table_name}"'/g' ${file}
        fi

    done < ${file}
done

sudo cp ${DATADIR}/db/tests/testdata/db/*.sql ${SCRIPTSDIR}/tests/testdata/db
