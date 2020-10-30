-- Revert nz-buildings:buildings_reference/add_nz_imagery_survey_index from pg

BEGIN;

DROP TABLE buildings_reference.nz_imagery_survey_index;

COMMIT;
