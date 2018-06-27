import processing


class Comparisons:
    """Class to provide processes to compare existing and
       incoming building outlines
    """
    def __init__(self, bulk_load_frame):
        """Constructor"""
        self.bulk_load_frame = bulk_load_frame

    def compare_outlines(self, commit_status):
        """Method called to compare outlines of current unprocessed dataset
        """
        self.bulk_load_frame.db.open_cursor()
        # find convex hull of supplied dataset outlines
        result = processing.runalg('qgis:convexhull',
                                   self.bulk_load_frame.bulk_load_layer,
                                   None, 0, None)
        convex_hull = processing.getObject(result['OUTPUT'])
        for feat in convex_hull.getFeatures():
            geom = feat.geometry()
            wkt = geom.exportToWkt()
            sql = 'SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193);'
            result = self.bulk_load_frame.db.execute_no_commit(sql, (wkt, ))
            geom = result.fetchall()[0][0]
        # Find intersecting buildings
        sql = 'SELECT * FROM buildings.building_outlines bo WHERE ST_Intersects(bo.shape, (SELECT ST_ConvexHull(ST_Collect(buildings_bulk_load.bulk_load_outlines.shape)) FROM buildings_bulk_load.bulk_load_outlines WHERE buildings_bulk_load.bulk_load_outlines.supplied_dataset_id = %s)) AND bo.building_outline_id NOT IN (SELECT building_outline_id FROM buildings_bulk_load.removed);'
        result = self.bulk_load_frame.db.execute_no_commit(sql,
                                                           (self.bulk_load_frame.current_dataset,))
        results = result.fetchall()

        if len(results) == 0:
            # No intersecting outlines
            sql = "SELECT bulk_load_outline_id FROM buildings_bulk_load.bulk_load_outlines blo WHERE blo.supplied_dataset_id = %s;"
            results = self.bulk_load_frame.db.execute_no_commit(sql,
                                                                (self.bulk_load_frame.current_dataset,))
            bulk_loaded_ids = results.fetchall()
            for id in bulk_loaded_ids:
                # add all incoming outlines to added table
                sql = 'SELECT buildings_bulk_load.added_insert_bulk_load_outlines(%s);'
                self.bulk_load_frame.db.execute_no_commit(sql, (id[0],))
            # update processed date
            sql = 'SELECT buildings_bulk_load.supplied_datasets_update_processed_date(%s);'
            result = self.bulk_load_frame.db.execute_no_commit(sql,
                                                               (self.bulk_load_frame.current_dataset,))

        else:
            # intersecting outlines exist
            for ls in results:
                sql = 'SELECT end_lifespan FROM buildings.building_outlines WHERE building_outline_id = %s;'
                life_span_check = self.bulk_load_frame.db.execute_no_commit(sql, (ls[0],))
                life_span_check = life_span_check.fetchall()[0][0]
                if life_span_check is None:
                    # If the outline is still 'active'
                    sql = 'SELECT building_outline_id FROM buildings_bulk_load.existing_subset_extracts WHERE building_outline_id = %s;'
                    result = self.bulk_load_frame.db.execute_no_commit(sql,
                                                                       (ls[0],
                                                                        ))
                    result = result.fetchall()
                    if len(result) == 0:
                        # insert new outline into existing subset extracts
                        sql = 'SELECT buildings_bulk_load.existing_subset_extracts_insert(%s, %s, %s);'
                        result = self.bulk_load_frame.db.execute_no_commit(sql,
                                                                           (ls[0],
                                                                            self.bulk_load_frame.current_dataset,
                                                                            ls[10]))
                    else:
                        # update supplied dataset id of existing outline
                        sql = 'SELECT buildings_bulk_load.existing_subset_extracts_update_supplied_dataset(%s, %s);'
                        self.bulk_load_frame.db.execute_no_commit(sql,
                                                                  (self.bulk_load_frame.current_dataset,
                                                                   ls[0]))
            # run comparisons function
            sql = 'SELECT buildings_bulk_load.compare_building_outlines(%s);'
            self.bulk_load_frame.db.execute_no_commit(sql,
                                                      (self.bulk_load_frame.current_dataset,))
        if commit_status:
            self.bulk_load_frame.db.commit_open_cursor()
