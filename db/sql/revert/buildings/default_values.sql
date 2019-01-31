-- Revert buildings:buildings/default_values from pg

BEGIN;

TRUNCATE buildings.lifecycle_stage CASCADE;

TRUNCATE buildings.use CASCADE;

COMMIT;
