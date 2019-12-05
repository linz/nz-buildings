# -*- coding: utf-8 -*-

import os.path

from functools import partial
from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSlot, Qt
from qgis.PyQt.QtWidgets import QFrame, QLineEdit, QMessageBox, QApplication, QCheckBox
from qgis.PyQt.QtGui import QIcon

from buildings.gui.error_dialog import ErrorDialog
from buildings.reference_data import topo50
from buildings.sql import buildings_bulk_load_select_statements as bulk_load_select
from buildings.sql import buildings_reference_select_statements as reference_select
from buildings.utilities import database as db

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "reference_data.ui")
)


class UpdateReferenceData(QFrame, FORM_CLASS):
    def __init__(self, dockwidget, parent=None):
        """Constructor."""
        super(UpdateReferenceData, self).__init__(parent)
        self.setupUi(self)
        self.dockwidget = dockwidget
        self.db = db
        self.db.connect()
        self.error_dialog = None
        self.message = ""
        self.msgbox = self.message_box()
        self.btn_view_key.setIcon(
            QIcon(os.path.join(__location__, "..", "icons", "view_password.png"))
        )

        # disable all check boxes if a curret dataset exists
        sql = bulk_load_select.supplied_dataset_latest_id_and_dates
        result = self.db.execute_return(sql)
        if result is None:
            self.enable_checkboxes()
            self.le_key.setDisabled(1)
            self.btn_view_key.setDisabled(1)
        else:
            result = result.fetchone()
            process = result[1]
            transfer = result[2]
            if process is not None and transfer is not None:
                self.enable_checkboxes()
                self.le_key.setDisabled(1)
                self.btn_view_key.setDisabled(1)
            else:
                self.disable_checkboxes()

        # set up signals and slots
        self.btn_view_key.pressed.connect(self.view_key)
        self.btn_view_key.released.connect(self.hide_key)
        self.le_key.editingFinished.connect(self.hide_key)
        self.grbx_topo.toggled.connect(self.check_all_topo)
        self.grbx_admin.toggled.connect(self.check_all_admin)
        self.btn_exit.clicked.connect(self.exit_clicked)
        self.btn_update.clicked.connect(
            partial(self.update_clicked, commit_status=True)
        )
        for box in self.grbx_topo.findChildren(QCheckBox):
            box.clicked.connect(self.chbx_clicked)

    def close_cursor(self):
        self.db.close_cursor()

    def connect(self):
        self.db.connect()

    def enable_checkboxes(self):
        """Enable frame"""
        self.grbx_topo.setEnabled(1)
        self.grbx_admin.setEnabled(1)
        self.chbx_canals.setEnabled(1)
        self.chbx_coastline_and_islands.setEnabled(1)
        self.chbx_lagoons.setEnabled(1)
        self.chbx_lakes.setEnabled(1)
        self.chbx_ponds.setEnabled(1)
        self.chbx_rivers.setEnabled(1)
        self.chbx_swamps.setEnabled(1)
        self.chbx_huts.setEnabled(1)
        self.chbx_shelters.setEnabled(1)
        self.chbx_bivouacs.setEnabled(1)
        self.chbx_protected_areas.setEnabled(1)
        self.chbx_suburbs.setEnabled(1)
        self.chbx_town.setEnabled(1)
        self.chbx_ta.setEnabled(1)
        self.btn_update.setEnabled(1)
        # clear message
        self.lb_message.setText("")

    def disable_checkboxes(self):
        """Disable frame (when outlines dataset in progress)"""
        self.le_key.setDisabled(1)
        self.grbx_topo.setDisabled(1)
        self.grbx_admin.setDisabled(1)
        self.chbx_canals.setDisabled(1)
        self.chbx_coastline_and_islands.setDisabled(1)
        self.chbx_lagoons.setDisabled(1)
        self.chbx_lakes.setDisabled(1)
        self.chbx_ponds.setDisabled(1)
        self.chbx_rivers.setDisabled(1)
        self.chbx_swamps.setDisabled(1)
        self.chbx_huts.setDisabled(1)
        self.chbx_shelters.setDisabled(1)
        self.chbx_bivouacs.setDisabled(1)
        self.chbx_protected_areas.setDisabled(1)
        self.chbx_suburbs.setDisabled(1)
        self.chbx_town.setDisabled(1)
        self.chbx_ta.setDisabled(1)
        self.btn_view_key.setDisabled(1)
        self.btn_update.setDisabled(1)
        # add message
        self.lb_message.setText(
            "\nNOTE: You can't update reference data with\n             a dataset in progress \n"
        )

    @pyqtSlot()
    def view_key(self):
        """Called when view key button pressed"""
        self.le_key.setEchoMode(QLineEdit.Normal)

    @pyqtSlot()
    def hide_key(self):
        """Called when view key button released/editing of text finished"""
        self.le_key.setEchoMode(QLineEdit.Password)

    @pyqtSlot()
    def update_clicked(self, commit_status=True):
        """Called when update btn clicked"""
        # set cursor to busy
        QApplication.setOverrideCursor(Qt.WaitCursor)
        # setup
        self.message = ""
        self.api_key = self.le_key.text()
        self.updates = []
        # canals
        if self.chbx_canals.isChecked():
            self.topo_layer_processing("canal_polygons")
        # lagoon
        if self.chbx_lagoons.isChecked():
            self.topo_layer_processing("lagoon_polygons")
        # lake
        if self.chbx_lakes.isChecked():
            self.topo_layer_processing("lake_polygons")
        # pond
        if self.chbx_ponds.isChecked():
            self.topo_layer_processing("pond_polygons")
        # rivers
        if self.chbx_rivers.isChecked():
            self.topo_layer_processing("river_polygons")
        # swamp
        if self.chbx_swamps.isChecked():
            self.topo_layer_processing("swamp_polygons")
        # huts
        if self.chbx_huts.isChecked():
            self.topo_layer_processing("hut_points")
        # shelters
        if self.chbx_shelters.isChecked():
            self.topo_layer_processing("shelter_points")
        # bivouacs
        if self.chbx_bivouacs.isChecked():
            self.topo_layer_processing("bivouac_points")
        # protected areas
        if self.chbx_protected_areas.isChecked():
            self.topo_layer_processing("protected_areas_polygons")
        # coastlines and islands (placeholder)
        if self.chbx_coastline_and_islands.isChecked():
            self.message += "The coastlines and islands table must be updated manually"
        if self.db._open_cursor is None:
            self.db.open_cursor()
        # suburb localities
        if self.chbx_suburbs.isChecked():
            suburb_list = []
            # delete existing suburbs where the external id is no longer in the suburb_locality table
            result = db.execute_no_commit(
                "SELECT buildings_reference.suburb_locality_delete_removed_areas();"
            )
            if result is not None:
                suburb_list.extend(result.fetchone()[0])
            # modify all existing areas to check they are up to date
            result = db.execute_no_commit(
                "SELECT buildings_reference.suburb_locality_insert_new_areas();"
            )
            if result is not None:
                suburb_list.extend(result.fetchone()[0])
            # insert into table ids in nz_localities that are not in suburb_locality
            result = db.execute_no_commit(
                "SELECT buildings_reference.suburb_locality_update_suburb_locality();"
            )
            if result is not None:
                suburb_list.extend(result.fetchone()[0])
            # update bulk_load_outlines suburb values
            db.execute_no_commit(
                "SELECT buildings_bulk_load.bulk_load_outlines_update_all_suburbs(%s);",
                (suburb_list,),
            )
            # update building_outlines suburb values
            db.execute_no_commit(
                "SELECT buildings.building_outlines_update_suburb(%s);", (suburb_list,)
            )
            # update messages and log
            self.update_message("updated", "suburb_locality")
            self.updates.append("suburb_locality")
        # town_city
        if self.chbx_town.isChecked():
            town_list = []
            # delete existing areas where the external id is no longer in the town_city table
            result = db.execute_no_commit(
                "SELECT buildings_reference.town_city_delete_removed_areas();"
            )
            if result is not None:
                town_list.extend(result.fetchone()[0])
            # modify all existing areas to check they are up to date
            result = db.execute_no_commit(
                "SELECT buildings_reference.town_city_insert_new_areas();"
            )
            if result is not None:
                town_list.extend(result.fetchone()[0])
            # insert into table ids in nz_localities that are not in town_city
            result = db.execute_no_commit(
                "SELECT buildings_reference.town_city_update_areas();"
            )
            if result is not None:
                town_list.extend(result.fetchone()[0])
            # update bulk_load_outlines town/city values
            db.execute_no_commit(
                "SELECT buildings_bulk_load.bulk_load_outlines_update_all_town_cities(%s);",
                (town_list,),
            )
            # update building outlines town/city values
            db.execute_no_commit(
                "SELECT buildings.building_outlines_update_town_city(%s);", (town_list,)
            )
            # update messages and log
            self.update_message("updated", "town_city")
            self.updates.append("town_city")
        # territorial authority and grid
        if self.chbx_ta.isChecked():
            ta_list = []
            # delete removed TA areas
            result = db.execute_no_commit(
                "SELECT buildings_reference.territorial_auth_delete_areas();"
            )
            if result is not None:
                ta_list.extend(result.fetchone()[0])
            # Insert TA areas
            result = db.execute_no_commit(
                "SELECT buildings_reference.territorial_auth_insert_areas();"
            )
            if result is not None:
                ta_list.extend(result.fetchone()[0])
            # Update new TA areas
            result = db.execute_no_commit(
                "SELECT buildings_reference.territorial_auth_update_areas();"
            )
            if result is not None:
                ta_list.extend(result.fetchone()[0])
            # update bulk_load_outlines territorial authority values
            db.execute_no_commit(
                "SELECT buildings_bulk_load.bulk_load_outlines_update_all_territorial_authorities(%s);",
                (ta_list,),
            )
            # update building outlines territorial authority values
            db.execute_no_commit(
                "SELECT buildings.building_outlines_update_territorial_authority(%s);",
                (ta_list,),
            )
            # update message and log
            self.update_message("updated", "territorial_authority")
            self.updates.append("territorial_authority")
            # refresh grid
            db.execute_no_commit(reference_select.refresh_ta_grid_view)
            self.update_message("updated", "territorial_authority_grid")
            self.updates.append("territorial_authority_grid")

        # create log for this update
        if len(self.updates) > 0:
            sql = "SELECT buildings_reference.reference_update_log_insert_log(%s);"
            self.db.execute_no_commit(sql, (self.updates,))
        # restore cursor
        QApplication.restoreOverrideCursor()
        # final message box
        if self.message == "":
            self.message = "No layers were updated."
        self.msgbox.setText(self.message)
        self.msgbox.exec_()
        if commit_status:
            self.db.commit_open_cursor()

    @pyqtSlot()
    def exit_clicked(self):
        """
        Called when new entry exit button clicked.
        """
        self.close_frame()
        self.dockwidget.lst_sub_menu.clearSelection()

    def close_frame(self):
        """
        Clean up and remove the new entry frame.
        """
        self.db.close_connection()
        from buildings.gui.menu_frame import MenuFrame

        dw = self.dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(MenuFrame(dw))

    @pyqtSlot()
    def check_all_topo(self):
        """ Called when combobox to check all topo layers is toggled"""
        if self.grbx_topo.isChecked():
            for box in self.grbx_topo.findChildren(QCheckBox):
                box.setChecked(True)
                box.setEnabled(1)
                self.chbx_clicked()
        else:
            for box in self.grbx_topo.findChildren(QCheckBox):
                box.setChecked(False)
                box.setEnabled(1)
                self.chbx_clicked()

    @pyqtSlot()
    def chbx_clicked(self):
        """Called when topo checkboxes are checked"""
        if not self.loop_topo_boxes():
            self.le_key.setDisabled(1)
            self.btn_view_key.setDisabled(1)

    def loop_topo_boxes(self):
        """loops through topo check boxes returns true if one is checked and enables api key features"""
        for box in self.grbx_topo.findChildren(QCheckBox):
            if box.isChecked():
                self.le_key.setEnabled(1)
                self.btn_view_key.setEnabled(1)
                return True
        return False

    @pyqtSlot()
    def check_all_admin(self):
        """ Called when combobox to check all admin layers is toggled"""
        if self.grbx_admin.isChecked():
            for box in self.grbx_admin.findChildren(QCheckBox):
                box.setChecked(True)
                box.setEnabled(1)
        else:
            for box in self.grbx_admin.findChildren(QCheckBox):
                box.setChecked(False)
                box.setEnabled(1)

    def message_box(self):
        return QMessageBox(
            QMessageBox.Information, "Note", self.message, buttons=QMessageBox.Ok
        )

    def request_error(self):
        """Called when failure to request a changeset"""
        self.error_dialog = ErrorDialog()
        self.error_dialog.fill_report(
            "\n ---------------------- REQUEST ERROR ---------"
            "----------------- \n\nSomething appears to have gone"
            " wrong with requesting the changeset, first please"
            " check you entered the correct api key if this is correct"
            " then please inform a developer."
        )
        self.error_dialog.show()
        QApplication.restoreOverrideCursor()

    def topo_layer_processing(self, layer):
        """Processes to run for all topo layers"""
        if not self.check_api_key():
            return
        status = topo50.update_topo50(self.api_key, layer)
        self.update_message(status, "{}_polygons".format(layer))
        if status != "error":
            self.updates.append(layer)

    def check_api_key(self):
        # check for API key
        if self.api_key == "":
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report(
                "\n------------- NO API KEY -------------"
                "\n\nPlease enter a koordinates api key to"
                " update the reference data."
            )
            self.error_dialog.show()
            QApplication.restoreOverrideCursor()
            return False
        return True

    def update_message(self, status, name):
        """add to message for display at end of processing"""
        if status == "current":
            self.message += "The {} table was up to date\n".format(name)
        if status == "updated":
            self.message += "The {} table has been updated\n".format(name)
        if status == "error":
            self.message += "The request errored on the {} table\n".format(name)
            self.request_error()
