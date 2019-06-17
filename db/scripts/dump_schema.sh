#!/bin/bash

export SCRIPTSDIR=/usr/share/nz-buildings/

while  true; do
    read -p 'PLUGIN [plugin] or DATABASE [db] schema dump?:' dump
    case "$dump" in
        "plugin")
            echo "Dumping Plugin Test Schema"
            database_name="nz-buildings-plugin-db"
            break
            ;;
        "db")
            echo "Dumping Database Test Schema"
            database_name="nz-buildings-pgtap-db"
            break
            ;;
        *)
            echo "Invalid Input" >&2
    esac
done

pg_dump --column-inserts --data-only --schema=admin_bdys ${database_name} > ${PWD}/db/tests/testdata/${dump}/admin_bdys.sql
pg_dump --column-inserts --data-only --schema=aerial_lds ${database_name} > ${PWD}/db/tests/testdata/${dump}/aerial_lds.sql
pg_dump --column-inserts --data-only --schema=buildings --exclude-table-data=buildings.lifecycle_stage --exclude-table-data=buildings.use ${database_name} > ${PWD}/db/tests/testdata/${dump}/buildings.sql
pg_dump --column-inserts --data-only --schema=buildings_common --exclude-table-data=buildings_common.capture_method --exclude-table-data=buildings_common.capture_source_group ${database_name} > ${PWD}/db/tests/testdata/${dump}/buildings_common.sql
pg_dump --column-inserts --data-only --schema=buildings_bulk_load --exclude-table-data=buildings_bulk_load.organisation --exclude-table-data=buildings_bulk_load.bulk_load_status --exclude-table-data=buildings_bulk_load.qa_status ${database_name} > ${PWD}/db/tests/testdata/${dump}/buildings_bulk_load.sql
pg_dump --column-inserts --data-only --schema=buildings_reference ${database_name} > ${PWD}/db/tests/testdata/${dump}/buildings_reference.sql
pg_dump --column-inserts --data-only --schema=buildings_lds ${database_name} > ${PWD}/db/tests/testdata/${dump}/buildings_lds.sql

echo "Cleaning and Copying dumped files:"
for file in ${PWD}/db/tests/testdata/${dump}/*.sql; do
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
sudo cp ${PWD}/db/tests/testdata/${dump}/*.sql ${SCRIPTSDIR}/tests/testdata/${dump}
