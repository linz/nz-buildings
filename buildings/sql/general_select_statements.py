"""
----------------------------------------------
General Select Statements not applicable
to any particular schema

- convert_geometry (geometry)
----------------------------------------------
"""

convert_geometry = """
SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193);
"""
