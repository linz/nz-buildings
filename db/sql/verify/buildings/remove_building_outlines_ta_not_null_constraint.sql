-- Verify nz-buildings:buildings/remove_building_outlines_ta_not_null_constraint on pg

BEGIN;

DO $$
DECLARE
    v_is_nullable boolean;
BEGIN
    SELECT is_nullable into v_is_nullable
    FROM information_schema.columns
    WHERE table_schema = 'buildings'
    AND table_name = 'building_outlines'
    AND column_name = 'territorial_authority_id';
        IF not v_is_nullable THEN
        RAISE EXCEPTION 'NOT-NULL CONSTRAINT: Schema "buildings" table "buildings" '
        'and column "territorial_authority_id" should not have not-null constraint';
    END IF;
END;
$$;

ROLLBACK;
