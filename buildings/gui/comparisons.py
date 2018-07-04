import processing
from buildings.sql import select_statements as select


def compare_outlines(self, commit_status):
    """
        Method called to compare outlines of current unprocessed dataset
    """
    self.db.open_cursor()
    feature_count = self.bulk_load_layer.featureCount()
    if feature_count < 100:
        result = processing.runalg(
            'qgis:convexhull', self.bulk_load_layer, None, 0, None)
        hull = processing.getObject(result['OUTPUT'])

    else:
        # extract polygon centroids
        result = processing.runalg(
            "qgis:polygoncentroids", self.bulk_load_layer, None)
        centroids = processing.getObject(result['OUTPUT_LAYER'])

        # use centroids to generate concave hull
        result = processing.runalg(
            "qgis:concavehull", centroids, 0.1, True,
            True, None, progress=None
        )

        hull = processing.getObject(result['OUTPUT'])

    results = []
    for feat in hull.getFeatures():
        geom = feat.geometry()
        wkt = geom.exportToWkt()
        sql = 'SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193);'
        result = self.db.execute_no_commit(sql, (wkt,))
        geom = result.fetchall()[0][0]
        # Find intersecting buildings
        result = self.db.execute_no_commit(
            select.building_outlines.format(geom))
        outlines = result.fetchall()
        for item in outlines:
            results.append(item)

    if len(results) == 0:
        # No intersecting outlines
        results = self.db.execute_no_commit(
            select.bulk_load_outlines_id_by_datasetID.format(
                self.current_dataset
            ))
        bulk_loaded_ids = results.fetchall()
        for id in bulk_loaded_ids:
            # add all incoming outlines to added table
            sql = 'SELECT buildings_bulk_load.added_insert_bulk_load_outlines(%s);'
            self.db.execute_no_commit(sql, (id[0],))
        # update processed date
        sql = 'SELECT buildings_bulk_load.supplied_datasets_update_processed_date(%s);'
        result = self.db.execute_no_commit(sql, (self.current_dataset,))

    else:
        # intersecting outlines exist
        for ls in results:
            life_span_check = self.db.execute_no_commit(
                select.building_outlines_end_lifespan_by_id.format(ls[0]))
            life_span_check = life_span_check.fetchall()[0][0]
            if life_span_check is None:
                # If the outline is still 'active'
                result = self.db.execute_no_commit(
                    select.existing_subset_extracts_by_building_outlineID.format(ls[0]))
                result = result.fetchall()
                if len(result) == 0:
                    # insert new outline into existing subset extracts
                    sql = 'SELECT buildings_bulk_load.existing_subset_extracts_insert(%s, %s, %s);'
                    result = self.db.execute_no_commit(
                        sql, (ls[0], self.current_dataset, ls[10]))
                else:
                    # update supplied dataset id of existing outline
                    sql = 'SELECT buildings_bulk_load.existing_subset_extracts_update_supplied_dataset(%s, %s);'
                    self.db.execute_no_commit(
                        sql, (self.current_dataset, ls[0]))
        # run comparisons function
        sql = 'SELECT buildings_bulk_load.compare_building_outlines(%s);'
        self.db.execute_no_commit(sql, (self.current_dataset,))
    if commit_status:
        self.db.commit_open_cursor()
