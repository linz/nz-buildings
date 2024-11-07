-- Revert nz-buildings:buildings_reference/add_log_column_nz_imagery_survey_index from pg

BEGIN;

ALTER TABLE buildings_reference.reference_update_log DROP COLUMN imagery_survey_index;

COMMIT;
