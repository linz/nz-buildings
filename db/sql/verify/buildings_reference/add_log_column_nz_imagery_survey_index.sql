-- Verify nz-buildings:buildings_reference/add_log_column_nz_imagery_survey_index on pg

BEGIN;

SELECT imagery_survey_index
FROM buildings_reference.reference_update_log
WHERE FALSE;

ROLLBACK;
