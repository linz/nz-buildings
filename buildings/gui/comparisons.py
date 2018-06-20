import processing


class Comparisons:

    def __init__(self, bulk_load_frame):
        self.bulk_lf = bulk_load_frame

    def compare_outlines(self, commit_status=True):
        self.bulk_lf.db.open_cursor()
        # find convex hull of supplied dataset outlines
        result = processing.runalg('qgis:convexhull',
                                   self.bulk_lf.bulk_load_layer,
                                   None, 0, None)
        convex_hull = processing.getObject(result['OUTPUT'])
        for feat in convex_hull.getFeatures():
            geom = feat.geometry()
            wkt = geom.exportToWkt()
            sql = 'SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193);'
            result = self.bulk_lf.db.execute_no_commit(sql, data=(wkt, ))
            geom = result.fetchall()[0][0]
        sql = 'SELECT * FROM buildings.building_outlines bo WHERE ST_Intersects(bo.shape, (SELECT ST_ConvexHull(ST_Collect(buildings_bulk_load.bulk_load_outlines.shape)) FROM buildings_bulk_load.bulk_load_outlines WHERE buildings_bulk_load.bulk_load_outlines.supplied_dataset_id = %s)) AND bo.building_outline_id NOT IN (SELECT building_outline_id FROM buildings_bulk_load.removed);'
        result = self.bulk_lf.db.execute_no_commit(sql,
                                                   (self.bulk_lf.current_dataset,))
        results = result.fetchall()
        if len(results) == 0:  # no existing outlines in this area
            # all new outlines
            sql = "SELECT bulk_load_outline_id FROM buildings_bulk_load.bulk_load_outlines blo WHERE blo.supplied_dataset_id = %s;"
            results = self.bulk_lf.db.execute_no_commit(sql,
                                                        (self.bulk_lf.current_dataset,))
            bulk_loaded_ids = results.fetchall()
            for id in bulk_loaded_ids:
                sql = 'SELECT buildings_bulk_load.added_insert_bulk_load_outlines(%s);'
                self.bulk_lf.db.execute_no_commit(sql, (id[0], ))
            sql = 'SELECT buildings_bulk_load.supplied_datasets_update_processed_date(%s);'
            result = self.bulk_lf.db.execute_no_commit(sql,
                                                       (self.bulk_lf.current_dataset,))
        else:
            for ls in results:
                sql = 'SELECT building_outline_id FROM buildings_bulk_load.existing_subset_extracts WHERE building_outline_id = %s;'
                result = self.bulk_lf.db.execute_no_commit(sql, (ls[0], ))
                result = result.fetchall()
                if len(result) == 0:
                    # insert relevant data into existing_subset_extract
                    sql = 'SELECT buildings_bulk_load.existing_subset_extracts_insert(%s, %s, %s);'
                    result = self.bulk_lf.db.execute_no_commit(sql, (ls[0],
                                                                     self.bulk_lf.current_dataset,
                                                                     ls[10]))
                else:
                    sql = 'SELECT buildings_bulk_load.existing_subset_extracts_update_supplied_dataset(%s, %s);'
                    self.bulk_lf.db.execute_no_commit(sql,
                                                      (self.bulk_lf.current_dataset,
                                                       ls[0]))
            # run comparisons function
            sql = 'SELECT buildings_bulk_load.compare_building_outlines(%s);'
            self.bulk_lf.db.execute_no_commit(sql,
                                              (self.bulk_lf.current_dataset,))
        if commit_status:
            self.bulk_lf.db.commit_open_cursor()
