-- Verify nz-buildings:buildings_bulk_load/remove_bulk_load_outlines_ta_not_null_constraint on pg

BEGIN;

DO $$
DECLARE
    v_is_nullable boolean;
BEGIN
    SELECT is_nullable into v_is_nullable
    FROM information_schema.columns
    WHERE table_schema = 'buildings_bulk_load'
    AND table_name = 'bulk_load_outlines'
    AND column_name = 'territorial_authority_id';
        IF not v_is_nullable THEN
        RAISE EXCEPTION 'NOT-NULL CONSTRAINT: Schema "buildings_bulk_load" table "bulk_load_outlines" '
        'and column "territorial_authority_id" should not have not-null constraint';
    END IF;
END;
$$;

ROLLBACK;
