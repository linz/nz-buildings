DO $$

DECLARE

  schema_name TEXT;
  table_name TEXT;
  primary_key_column TEXT;

BEGIN

  -- Loop through all tables in specified database
  FOR schema_name, table_name IN (
    SELECT tables.table_schema, tables.table_name
    FROM information_schema.tables
    WHERE table_catalog='nz-buildings-pgtap-db'
  ) LOOP

    -- Get the primary key column for each table
    SELECT pg_attribute.attname INTO primary_key_column
    FROM pg_index, pg_class, pg_attribute, pg_namespace
    WHERE pg_class.oid =  (schema_name||'.'||table_name)::regclass
    AND indrelid = pg_class.oid
    AND pg_class.relnamespace = pg_namespace.oid
    AND pg_attribute.attrelid = pg_class.oid
    AND pg_attribute.attnum = any(pg_index.indkey)
    AND indisprimary;

    -- Check if a sequence exists for that primary key column
    IF ''||table_name||'_'||primary_key_column||'_seq' IN (
      SELECT sequences.sequence_name
      FROM information_schema.sequences
    ) THEN
      IF ''||schema_name||'.'||table_name||'' IN ('buildings.buildings', 'buildings.building_outlines', 'buildings.building_name', 'buildings.building_use', 'buildings.lifecycle', 'buildings_bulk_load.supplied_outlines', 'buildings_bulk_load.bulk_load_outlines') THEN
        EXECUTE 'SELECT setval(
                 '''||schema_name||'.'||table_name||'_'||primary_key_column||'_seq'',
                 GREATEST((SELECT max('||primary_key_column||') FROM '||schema_name||'.'||table_name||')+1, 1000000), false)';
      ELSE
        -- Update the sequence based on the max value from that table + 1
        EXECUTE 'SELECT setval(
                   '''||schema_name||'.'||table_name||'_'||primary_key_column||'_seq'',
                   (SELECT max('||primary_key_column||') FROM '||schema_name||'.'||table_name||')+1
                 )';
      END IF;

    END IF;

  END LOOP;

END
$$;
