DO $$
DECLARE
i TEXT;
j TEXT;
k TEXT;
BEGIN
    FOR i, j IN (select table_schema, table_name from information_schema.tables where table_catalog='nz-buildings-pgtap-db') LOOP
    SELECT
      pg_attribute.attname INTO k
    FROM pg_index, pg_class, pg_attribute, pg_namespace
    WHERE
      pg_class.oid =  (i || '.' || j)::regclass AND
      indrelid = pg_class.oid AND
      pg_class.relnamespace = pg_namespace.oid AND
      pg_attribute.attrelid = pg_class.oid AND
      pg_attribute.attnum = any(pg_index.indkey)
     AND indisprimary;
    IF ''||j||'_'||k||'_seq' IN (SELECT sequence_name FROM information_schema.sequences) then
            EXECUTE 'Select setval(('''||i||'.'||j||'_'||k||'_seq''), (SELECT max('||k||') FROM ' || i || '.' || j ||')+1)';
    END IF;
    END LOOP;
END$$;
