-- Deploy nz-buildings:buildings_reference/add_log_column_nz_imagery_survey_index to pg

BEGIN;

ALTER TABLE buildings_reference.reference_update_log ADD imagery_survey_index boolean DEFAULT False;

COMMIT;
