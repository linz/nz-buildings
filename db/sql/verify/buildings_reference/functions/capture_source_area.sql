-- Verify nz-buildings:buildings_reference/functions/capture_source_area on pg

BEGIN;

SELECT has_function_privilege(
      'buildings_reference.capture_source_area_insert(varchar(250), varchar(250), geometry)'
    , 'execute'  
);

ROLLBACK;
