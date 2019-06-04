#!/bin/bash

export SCRIPTSDIR=/usr/share/nz-buildings/

# dump all the schema
pg_dump --column-inserts --data-only --schema=admin_bdys nz-buildings-pgtap-db > ${PWD}/db/tests/testdata/db/admin_bdys.sql
pg_dump --column-inserts --data-only --schema=aerial_lds nz-buildings-pgtap-db > ${PWD}/db/tests/testdata/db/aerial_lds.sql
pg_dump --column-inserts --data-only --schema=buildings nz-buildings-pgtap-db > ${PWD}/db/tests/testdata/db/buildings.sql
pg_dump --column-inserts --data-only --schema=buildings_common nz-buildings-pgtap-db > ${PWD}/db/tests/testdata/db/buildings_common.sql
pg_dump --column-inserts --data-only --schema=buildings_bulk_load nz-buildings-pgtap-db > ${PWD}/db/tests/testdata/db/buildings_bulk_load.sql
pg_dump --column-inserts --data-only --schema=buildings_reference nz-buildings-pgtap-db > ${PWD}/db/tests/testdata/db/buildings_reference.sql
pg_dump --column-inserts --data-only --schema=buildings_lds nz-buildings-pgtap-db > ${PWD}/db/tests/testdata/db/buildings_lds.sql

for file in ${PWD}/db/tests/testdata/db/*.sql; do
    echo ${file} >&2
    # remove lines that start with SET
    sed -i '/^SET/ d' ${file}
    # remove lines that start with SELECT
    sed -i '/^SELECT/ d' ${file}
    # remove all lines that are solely '--'
    sed -i '/--$/ d' ${file}
    # remove all comments not about table data
    sed -i '/--/ {/TABLE DATA/! d}' ${file}
    # remove all empty lines
    sed -i '/^$/ d' ${file}
    # insert one empty line above all remaining comments
    sed -i '/^--/ i \\' ${file}
    # append one empty line after all remaining comments
    sed -i '/^--/ a \\' ${file}
    # loop through file and reformat data table description comments
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

# copy tables over to usr/share folder location
sudo cp ${PWD}/db/tests/testdata/db/*.sql ${SCRIPTSDIR}/tests/testdata/db
