# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtGui import QFrame
import qgis

from buildings.utilities import database as db

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "new_outline.ui"))

db.connect()


class NewOutline(QFrame, FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super(NewOutline, self).__init__(parent)
        self.setupUi(self)
        self.populate_lookup_comboboxes()
        self.populate_area_comboboxes()
        # add building_outlines layer to canvas
        # allow editing of building outlines layer

        # set up signals
        self.btn_save.clicked.connect(self.save_clicked)
        self.btn_reset.clicked.connect(self.reset_clicked)
        self.btn_cancel.clicked.connect(self.cancel_clicked)

    def populate_lookup_comboboxes(self):
        # populate capture method combobox
        sql = "SELECT value FROM buildings_common.capture_method;"
        result = db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            self.cmb_capture_method.addItem(item[0])
        # populate lifecycle stage combobox
        sql = "SELECT value FROM buildings.lifecycle_stage;"
        result = db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            self.cmb_lifecycle_stage.addItem(item[0])

        # populate capture source group
        sql = "SELECT csg.value, csg.description, cs.external_source_id FROM buildings_common.capture_source_group csg, buildings_common.capture_source cs WHERE cs.capture_source_group_id = csg.capture_source_group_id;"
        result = db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            text = str(item[0]) + '- ' + str(item[1] + '- ' + str(item[2]))
            self.cmb_capture_source.addItem(text)

    def populate_area_comboboxes(self):
        # TODO is only Wellington
        # populate suburb combobox
        sql = "SELECT DISTINCT alias_name FROM admin_bdys.suburb_alias"
        result = db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            if item[0] is not None:
                self.cmb_suburb.addItem(item[0])

        # populate town combobox
        sql = "SELECT DISTINCT city_name FROM admin_bdys.nz_locality"
        result = db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            if item[0] is not None:
                self.cmb_town.addItem(item[0])

        sql = "SELECT DISTINCT name FROM admin_bdys.territorial_authority"
        result = db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            if item[0] is not None:
                self.cmb_ta.addItem(item[0])

    def get_capture_method_id(self):
        index = self.cmb_capture_method.currentIndex()
        text = self.cmb_capture_method.itemText(index)
        sql = "SELECT capture_method_id FROM buildings_common.capture_method cm WHERE cm.value = %s;"
        result = db._execute(sql, data=(text, ))
        return result.fetchall()[0][0]

    def get_lifecycle_stage_id(self):
        index = self.cmb_lifecycle_stage.currentIndex()
        text = self.cmb_lifecycle_stage.itemText(index)
        sql = "SELECT lifecycle_stage_id FROM buildings.lifecycle_stage ls WHERE ls.value = %s;"
        result = db._execute(sql, data=(text, ))
        return result.fetchall()[0][0]

    def get_capture_source_id(self):
        index = self.cmb_capture_source.currentIndex()
        text = self.cmb_capture_source.itemText(index)
        text_ls = text.split('- ')
        sql = "SELECT capture_source_group_id FROM buildings_common.capture_source_group csg WHERE csg.value = %s AND csg.description = %s;"
        result = db._execute(sql, data=(text_ls[0], text_ls[1]))
        data = result.fetchall()[0][0]
        sql = "SELECT capture_source_id FROM buildings_common.capture_source cs WHERE cs.capture_source_group_id = %s and cs.external_source_id = %s;"
        result = db._execute(sql, data=(data, text_ls[2]))
        return result.fetchall()[0][0]

    def get_suburb(self):
        print 'something'

    def get_town(self):
        print 'something'

    def get_t_a(self):
        index = self.cmb_capture_method.currentIndex()
        return self.cmb_capture_method.itemText(index)

    def save_clicked(self):
        self.capture_source_id = self.get_capture_source_id()
        self.lifecycle_stage_id = self.get_lifecycle_stage_id()
        self.capture_method_id = self.get_capture_method_id()

        self.suburb = None  # self.get_suburb()
        self.town = None  # self.get_town()
        self.t_a = self.get_t_a()

        # fail if change shape of existing geom?
        # fail if drawn multiple geoms?

        # take geom of outline drawn
        # update buildings
            # new id, begin lifespan now()
        # update building_outlines:
            # new_id, building_id, combobox values (capture_method, capture_source, lifecycle stage, suburb, town, TA), begin_lifespan now(), drawn geom  

        print 'save'

    def cancel_clicked(self):
        from buildings.gui.menu_frame import MenuFrame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(MenuFrame)

    def reset_clicked(self):
        print 'reset'
