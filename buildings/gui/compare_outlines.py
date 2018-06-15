# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtGui import QFrame

import qgis
from qgis.utils import iface
from qgis.core import QgsVectorLayer

import processing

from functools import partial

from buildings.gui.error_dialog import ErrorDialog
from buildings.utilities import database as db

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'compare_outlines.ui'))


class CompareOutlines(QFrame, FORM_CLASS):

    # set up
    value = ''
    dataset_id = None
    layer = None

    def __init__(self, layer_registry, parent=None):
        """Constructor."""
        super(CompareOutlines, self).__init__(parent)
        self.setupUi(self)

        self.db = db
        self.db.connect()

        self.populate_dataset_combobox()

        self.layer_registry = layer_registry
        self.building_layer = QgsVectorLayer()
        self.find_dataset()
        # signals and slots
        self.cmb_supplied_dataset.currentIndexChanged.connect(self.find_dataset)
        self.btn_ok.clicked.connect(partial(self.ok_clicked,
                                            commit_status=True))
        self.btn_exit.clicked.connect(self.exit_clicked)

    def populate_dataset_combobox(self):
        sql = 'SELECT supplied_dataset_id, description FROM buildings_bulk_load.supplied_datasets sd WHERE sd.processed_date is NULL;'
        results = self.db._execute(sql)
        datasets = results.fetchall()
        for dset in datasets:
            text = '{0}-{1}'.format(dset[0], dset[1])
            self.cmb_supplied_dataset.addItem(text)
        if len(datasets) == 0:
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report('\n ---------------- NO '
                                          'UNPROCESSED DATASETS -----'
                                          '----------- \n\n There '
                                          'are no unprocessed datasets '
                                          'please load some outlines '
                                          'first'
                                          )
            self.error_dialog.show()
            self.cmb_supplied_dataset.setDisabled(1)

    def find_dataset(self):
        """Called when supplied dataset index is changed"""
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            'styles/')
        text = self.cmb_supplied_dataset.currentText()
        text_list = text.split('-')
        self.dataset_id = text_list[0]
        sql = 'SELECT count(*) FROM buildings_bulk_load.bulk_load_outlines WHERE supplied_dataset_id = %s;'
        result = self.db._execute(sql, (self.dataset_id))
        result = result.fetchall()[0][0]
        self.lb_outlines.setText(str(result))
        self.layer_registry.remove_layer(self.building_layer)
        # add the bulk_load_outlines to the layer registry
        self.building_layer = self.layer_registry.add_postgres_layer(
            'bulk_load_outlines', 'bulk_load_outlines',
            'shape', 'buildings_bulk_load', '',
            'supplied_dataset_id = {0}'.format(self.dataset_id)
        )
        self.building_layer.loadNamedStyle(path + 'building_yellow.qml')
        iface.setActiveLayer(self.building_layer)

    def ok_clicked(self, commit_status):
        # check imagery field and value are not null
        self.db.open_cursor()
        # find convex hull of supplied dataset outlines
        result = processing.runalg('qgis:convexhull', self.building_layer,
                                   None, 0, None)
        convex_hull = processing.getObject(result['OUTPUT'])
        for feat in convex_hull.getFeatures():
            geom = feat.geometry()
            wkt = geom.exportToWkt()
            sql = 'SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193);'
            result = self.db.execute_no_commit(sql, data=(wkt, ))
            geom = result.fetchall()[0][0]
        # iterate through supplied datasets and find convex hulls
        sql = 'SELECT max(supplied_dataset_id) FROM buildings_bulk_load.supplied_datasets;'
        result = self.db.execute_no_commit(sql)
        max_dataset_id = result.fetchall()[0][0]
        dataset = 1
        self.bulk_overlap = False
        while dataset <= max_dataset_id:
            """
            TODO
            # transfered date
            sql = 'SELECT transfer_date FROM buildings_bulk_load.supplied_datasets WHERE supplied_dataset_id = %s;'
            results = self.db.execute_no_commit(sql, (dataset, ))
            t_date = results.fetchall()[0][0]
            # imagery_date = sql (TODO)
            if t_date:
                if t_date is None:
                    if imagery_date is earlier than current dataset imagery_date: (TODO)
                        sql = 'SELECT * FROM buildings_bulk_load.bulk_load_outlines outlines WHERE ST_Intersects(%s, (SELECT ST_ConvexHull(ST_Collect(buildings_bulk_load.bulk_load_outlines.shape)) FROM buildings_bulk_load.bulk_load_outlines WHERE buildings_bulk_load.bulk_load_outlines.supplied_dataset_id = %s));'
                        result = self.db.execute_no_commit(sql, data=(geom,
                                                              dataset))
                        results = result.fetchall()
                        # if there are intersecting buildings
                        if len(results) > 0:
                            self.bulk_overlap = True
                            break
                    else:
                        pass
                else:
                    pass
            """
            dataset = dataset + 1
            if self.bulk_overlap is True:
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report('\n ---------------- BULK '
                                              'LOAD OVERLAP ------------'
                                              '-- \n\n An earlier unprocessed'
                                              ' bulk loaded dataset with '
                                              'dataset id of {0} overlaps '
                                              'this dataset please process'
                                              ' this first'.format(dataset)
                                              )
                self.error_dialog.show()
                self.db.rollback_open_cursor()
                return
        # sql = 'SELECT * FROM buildings.building_outlines bo WHERE ST_Intersects(bo.shape, (SELECT ST_ConvexHull(ST_Collect(buildings_bulk_load.bulk_load_outlines.shape)) FROM buildings_bulk_load.bulk_load_outlines WHERE buildings_bulk_load.bulk_load_outlines.supplied_dataset_id = %s));'
        sql = 'SELECT * FROM buildings.building_outlines bo WHERE ST_Intersects(bo.shape, (SELECT ST_ConvexHull(ST_Collect(buildings_bulk_load.bulk_load_outlines.shape)) FROM buildings_bulk_load.bulk_load_outlines WHERE buildings_bulk_load.bulk_load_outlines.supplied_dataset_id = %s)) AND bo.building_outline_id NOT IN (SELECT building_outline_id FROM buildings_bulk_load.removed);'
        result = self.db.execute_no_commit(sql, data=(self.dataset_id, ))
        results = result.fetchall()
        if len(results) == 0:  # no existing outlines in this area
            # all new outlines
            sql = "SELECT bulk_load_outline_id FROM buildings_bulk_load.bulk_load_outlines blo WHERE blo.supplied_dataset_id = %s;"
            results = self.db.execute_no_commit(sql, (self.dataset_id, ))
            bulk_loaded_ids = results.fetchall()
            for id in bulk_loaded_ids:
                sql = 'INSERT INTO buildings_bulk_load.added(bulk_load_outline_id, qa_status_id) VALUES(%s, 1);'
                self.db.execute_no_commit(sql, (id[0], ))
        else:
            for ls in results:
                sql = 'SELECT building_outline_id FROM buildings_bulk_load.existing_subset_extracts WHERE building_outline_id = %s;'
                result = self.db.execute_no_commit(sql, (ls[0], ))
                result = result.fetchall()
                if len(result) == 0:
                    # insert relevant data into existing_subset_extract
                    sql = 'SELECT buildings_bulk_load.existing_subset_extracts_insert(%s, %s, %s);'
                    result = self.db.execute_no_commit(sql, data=(ls[0],
                                                       self.dataset_id,
                                                       ls[10]))
                else:
                    sql = 'UPDATE buildings_bulk_load.existing_subset_extracts SET supplied_dataset_id = %s WHERE building_outline_id = %s;'
                    self.db.execute_no_commit(sql, (self.dataset_id, ls[0]))
            # run comparisons function
            sql = 'SELECT buildings_bulk_load.compare_building_outlines(%s);'
            self.db.execute_no_commit(sql, data=(self.dataset_id, ))
        if commit_status:
            self.db.commit_open_cursor()

    def exit_clicked(self):
        """Called when exit button is clicked"""
        self.db.close_connection()
        if self.building_layer in self.layer_registry.layers.values():
            self.layer_registry.remove_layer(self.building_layer)
        from buildings.gui.menu_frame import MenuFrame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(MenuFrame(self.layer_registry))
