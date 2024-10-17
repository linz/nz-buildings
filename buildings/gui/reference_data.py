# -*- coding: utf-8 -*-

import os.path

from functools import partial
from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSlot, Qt
from qgis.PyQt.QtWidgets import QFrame, QLineEdit, QMessageBox, QApplication, QCheckBox
from qgis.PyQt.QtGui import QIcon

from buildings.gui.error_dialog import ErrorDialog
from buildings.reference_data import topo50, admin_bdys
from buildings.sql import buildings_bulk_load_select_statements as bulk_load_select
from buildings.sql import buildings_reference_select_statements as reference_select
from buildings.utilities import database as db
from buildings.utilities.warnings import buildings_warning
from buildings.utilities.config import read_config_file

try:
    DB_CONFIG = read_config_file()["api"]
except RuntimeError as error:
    buildings_warning("Config file error", str(error), "critical")
    raise error
API_KEY_LINZ = DB_CONFIG["linz"]
API_KEY_STATSNZ = DB_CONFIG["statsnz"]

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "reference_data.ui")
)

DATASET_LINZ = [
    "canal_polygons",
    "lagoon_polygons",
    "lake_polygons",
    "pond_polygons",
    "river_polygons",
    "swamp_polygons",
    "hut_points",
    "shelter_points",
    "bivouac_points",
    "protected_areas_polygons",
    "coastlines_and_islands",
    "suburb_locality",
]
DATASET_STATSNZ = ["territorial_authority"]


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

        # disable all check boxes if a curret dataset exists
        sql = bulk_load_select.supplied_dataset_latest_id_and_dates
        result = self.db.execute_return(sql)
        if result is None:
            self.enable_checkboxes()
        else:
            result = result.fetchone()
            process = result[1]
            transfer = result[2]
            if process is not None and transfer is not None:
                self.enable_checkboxes()
            else:
                self.disable_checkboxes()

        # set up signals and slots
        self.grbx_topo.toggled.connect(self.check_all_topo)
        self.grbx_admin.toggled.connect(self.check_all_admin)
        self.btn_exit.clicked.connect(self.exit_clicked)
        self.btn_update.clicked.connect(
            partial(self.update_clicked, commit_status=True)
        )

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
        self.chbx_ta.setEnabled(1)
        self.btn_update.setEnabled(1)
        # clear message
        self.lb_message.setText("")

    def disable_checkboxes(self):
        """Disable frame (when outlines dataset in progress)"""
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
        self.chbx_ta.setDisabled(1)
        self.btn_update.setDisabled(1)
        # add message
        self.lb_message.setText(
            "\nNOTE: You can't update reference data with\n             a dataset in progress \n"
        )

    @pyqtSlot()
    def update_clicked(self, commit_status=True):
        """Called when update btn clicked"""
        # set cursor to busy
        QApplication.setOverrideCursor(Qt.WaitCursor)
        # setup
        self.message = ""
        self.updates = []
        if self.db._open_cursor is None:
            self.db.open_cursor()
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
        # coastlines and islands (overwrite the existing table)
        if self.chbx_coastline_and_islands.isChecked():
            self.topo_layer_processing("coastlines_and_islands")
        # suburb localities
        if self.chbx_suburbs.isChecked():
            self.admin_bdy_layer_processing("suburb_locality")
        # territorial authority and grid
        if self.chbx_ta.isChecked():
            self.admin_bdy_layer_processing("territorial_authority")

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
        """Called when combobox to check all topo layers is toggled"""
        if self.grbx_topo.isChecked():
            for box in self.grbx_topo.findChildren(QCheckBox):
                box.setChecked(True)
                box.setEnabled(1)
        else:
            for box in self.grbx_topo.findChildren(QCheckBox):
                box.setChecked(False)
                box.setEnabled(1)

    @pyqtSlot()
    def check_all_admin(self):
        """Called when combobox to check all admin layers is toggled"""
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
            " check you entered the correct api key in config file"
            " then please inform a developer."
        )
        self.error_dialog.show()
        QApplication.restoreOverrideCursor()

    def topo_layer_processing(self, dataset):
        """Processes to run for topo layers"""
        api_key = self.check_api_key(dataset)
        if api_key is None:
            return
        if dataset == "coastlines_and_islands":
            status = topo50.update_coastlines_and_islands(api_key, dataset, self.db)
        else:
            status = topo50.update_topo50(api_key, dataset, self.db)
        self.update_message(status, dataset)
        if status != "error":
            self.updates.append(dataset)

    def admin_bdy_layer_processing(self, dataset):
        """Processes to run for admin bdy layers"""
        api_key = self.check_api_key(dataset)
        if api_key is None:
            return
        status = admin_bdys.update_admin_bdys(api_key, dataset, self.db)
        self.update_message(status, dataset)
        if status != "error":
            self.updates.append(dataset)
            if dataset == "territorial_authority":
                self.db.execute_no_commit(reference_select.refresh_ta_grid_view)
                self.update_message("updated", "territorial_authority_grid")
                self.updates.append("territorial_authority_grid")

    def check_api_key(self, layer):
        # check for API key
        if layer in DATASET_LINZ:
            return API_KEY_LINZ
        elif layer in DATASET_STATSNZ:
            return API_KEY_STATSNZ
        self.error_dialog = ErrorDialog()
        self.error_dialog.fill_report(
            "\n------------- NO API KEY -------------"
            "\n\nPlease enter a koordinates api key to"
            " update the reference data."
        )
        self.error_dialog.show()
        QApplication.restoreOverrideCursor()
        return None

    def update_message(self, status, name):
        """add to message for display at end of processing"""
        if status == "current":
            self.message += "The {} table was up to date\n".format(name)
        if status == "updated":
            self.message += "The {} table has been updated\n".format(name)
        if status == "error":
            self.message += "The request errored on the {} table\n".format(name)
            self.request_error()
