
# -*- coding: utf-8 -*-

from functools import partial
import math
import os.path

from PyQt4 import uic
from PyQt4.QtCore import pyqtSignal, pyqtSlot, QSize, Qt
from PyQt4.QtGui import QAction, QApplication, QColor, QFrame, QIcon, QMenu, QMessageBox
from qgis.core import QgsFeature, QgsGeometry, QgsPoint, QgsProject, QgsVectorLayer, QgsMapLayerRegistry
from qgis.gui import QgsMessageBar, QgsRubberBand
from qgis.utils import iface

from buildings.gui import bulk_load, bulk_load_changes, comparisons
from buildings.gui.alter_building_relationships import AlterRelationships
from buildings.gui.check_dialog import CheckDialog
from buildings.gui.edit_dialog import EditDialog
from buildings.gui.error_dialog import ErrorDialog
from buildings.sql import (buildings_bulk_load_select_statements as bulk_load_select,
                           buildings_common_select_statements as common_select,
                           buildings_reference_select_statements as reference_select)
from buildings.utilities import database as db
from buildings.utilities.layers import LayerRegistry
from buildings.utilities.point_tool import PointTool

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'bulk_load.ui'))


class BulkLoadFrame(QFrame, FORM_CLASS):
    """Bulk Load outlines frame class"""

    closed = pyqtSignal()

    def __init__(self, dockwidget, parent=None):
        """Constructor."""

        super(BulkLoadFrame, self).__init__(parent)
        self.setupUi(self)
        # Frame fields
        self.dockwidget = dockwidget
        self.layer_registry = LayerRegistry()
        self.bulk_load_layer = QgsVectorLayer()
        self.territorial_auth = QgsVectorLayer()
        # Set up pop-up dialog
        self.check_dialog = CheckDialog()
        self.error_dialog = None
        self.edit_dialog = None
        # bulk load changes instance
        self.change_instance = None
        # layer set up
        self.historic_layer = None
        self.bulk_load_layer = None
        self.territorial_auth = None
        # database setup
        self.db = db
        db.connect()
        # selection colour
        iface.mapCanvas().setSelectionColor(QColor('Yellow'))
        # set up confirmation message box
        self.msgbox_bulk_load = self.confirmation_dialog_box('bulk load')
        self.msgbox_compare = self.confirmation_dialog_box('compare')
        self.msgbox_publish = self.confirmation_dialog_box('publish')
        self.grpb_layers.hide()

        # Find current supplied dataset
        result = self.db._execute(bulk_load_select.supplied_dataset_count_processed_date_is_null)
        result = result.fetchall()[0][0]
        # if there is an unprocessed dataset
        if result > 1:
            # error
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report(
                '\n ---------------------- DATASET ERROR ---------'
                '----------------- \n\nThere are multiple not processed'
                ' datasets. Please fix database tables before continuing'
            )
            self.error_dialog.show()
            self.display_dataset_error()

        elif result == 1:
            p_result = self.db._execute(bulk_load_select.supplied_dataset_processed_date_is_null)
            self.current_dataset = p_result.fetchall()[0][0]
            self.lb_dataset_id.setText(str(self.current_dataset))
            self.add_outlines()
            self.display_current_bl_not_compared()
            self.grpb_layers.show()
            # Setup edit dialog
            self.edit_dialog = EditDialog(self)

        # if all datasets are processed
        else:
            result2 = self.db._execute(bulk_load_select.supplied_dataset_count_transfer_date_is_null)
            result2 = result2.fetchall()[0][0]

            # if there is a processed but not transferred dataset
            if result > 1:
                # error
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report(
                    '\n ---------------------- DATASET ERROR ---------'
                    '----------------- \n\nThere are multiple not transferred'
                    ' datasets. Please fix database tables before continuing'
                )
                self.error_dialog.show()
                self.display_dataset_error()

            elif result2 == 1:
                t_result = self.db._execute(bulk_load_select.supplied_dataset_transfer_date_is_null)
                self.current_dataset = t_result.fetchall()[0][0]
                self.lb_dataset_id.setText(str(self.current_dataset))
                self.add_outlines()
                self.display_not_published()
                self.grpb_layers.show()
                # Setup edit dialog
                self.edit_dialog = EditDialog(self)

            # No current dataset is being worked on
            else:
                self.current_dataset = None
                self.lb_dataset_id.setText('None')
                self.display_no_bulk_load()
                self.cmb_capture_src_grp.currentIndexChanged.connect(self.cmb_capture_src_grp_changed)

        # initiate le_data_description
        self.le_data_description.setMaxLength(250)
        self.le_data_description.setPlaceholderText('Data Description')

        # set up signals and slots
        self.rad_external_id.toggled.connect(
            partial(bulk_load.enable_external_bulk, self))
        self.ml_outlines_layer.currentIndexChanged.connect(
            partial(bulk_load.populate_external_fcb, self))
        self.btn_bl_save.clicked.connect(
            partial(self.bulk_load_save_clicked, True))
        self.btn_bl_reset.clicked.connect(self.bulk_load_reset_clicked)

        self.btn_compare_outlines.clicked.connect(
            partial(self.compare_outlines_clicked, True))

        self.btn_alter_rel.clicked.connect(self.alter_relationships_clicked)
        self.btn_publish.clicked.connect(partial(self.publish_clicked, True))
        self.btn_exit.clicked.connect(self.exit_clicked)

        self.cb_bulk_load.clicked.connect(self.cb_bulk_load_clicked)
        self.cb_removed.clicked.connect(self.cb_removed_clicked)
        self.cb_added.clicked.connect(self.cb_added_clicked)

        QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.layers_removed)

    def confirmation_dialog_box(self, button_text):
        return QMessageBox(QMessageBox.Question, button_text.upper(),
                           'Are you sure you want to %s outlines?' % button_text, buttons=QMessageBox.No | QMessageBox.Yes)

    def confirm(self, msgbox):
        reply = msgbox.exec_()
        if reply == QMessageBox.Yes:
            return True
        return False

    def setup_toolbar(self):

        if 'Add Outline' not in (action.text() for action in iface.building_toolbar.actions()):
            image_dir = os.path.join(__location__, '..', 'icons')
            icon_path = os.path.join(image_dir, "plus.png")
            icon = QIcon()
            icon.addFile(icon_path, QSize(8, 8))
            self.add_action = QAction(icon, "Add Outline", iface.building_toolbar)
            iface.registerMainWindowAction(self.add_action, "Ctrl+1")
            self.add_action.triggered.connect(self.canvas_add_outline)
            iface.building_toolbar.addAction(self.add_action)

        if 'Edit Geometry' not in (action.text() for action in iface.building_toolbar.actions()):
            image_dir = os.path.join(__location__, '..', 'icons')
            icon_path = os.path.join(image_dir, "edit_geometry.png")
            icon = QIcon()
            icon.addFile(icon_path, QSize(8, 8))
            self.edit_geom_action = QAction(icon, "Edit Geometry", iface.building_toolbar)
            iface.registerMainWindowAction(self.edit_geom_action, "Ctrl+2")
            self.edit_geom_action.triggered.connect(self.canvas_edit_geometry)
            iface.building_toolbar.addAction(self.edit_geom_action)

        if 'Edit Attributes' not in (action.text() for action in iface.building_toolbar.actions()):
            image_dir = os.path.join(__location__, '..', 'icons')
            icon_path = os.path.join(image_dir, "edit_attributes.png")
            icon = QIcon()
            icon.addFile(icon_path, QSize(8, 8))
            self.edit_attrs_action = QAction(icon, "Edit Attributes", iface.building_toolbar)
            iface.registerMainWindowAction(self.edit_attrs_action, "Ctrl+3")
            self.edit_attrs_action.triggered.connect(self.canvas_edit_attribute)
            iface.building_toolbar.addAction(self.edit_attrs_action)

        iface.building_toolbar.show()

    def display_dataset_error(self):
        """UI Display when there are multiple supplied datasets."""

        self.current_dataset = None
        self.lb_dataset_id.setText('None')

        self.grpb_bulk_load.hide()
        iface.building_toolbar.hide()

        self.btn_compare_outlines.setDisabled(1)
        self.btn_alter_rel.setDisabled(1)
        self.btn_publish.setDisabled(1)

    def display_no_bulk_load(self):
        """UI Display When there is no Current dataset."""

        self.grpb_bulk_load.show()
        bulk_load.populate_bulk_comboboxes(self)
        self.ml_outlines_layer.setEnabled(1)
        self.rad_external_id.setEnabled(1)
        self.rad_external_id.setChecked(False)
        self.fcb_external_id.setDisabled(1)
        self.cmb_capture_src_grp.setEnabled(1)
        self.cmb_capture_src_grp.setCurrentIndex(0)
        self.cmb_cap_src_area.setEnabled(1)
        self.le_data_description.setEnabled(1)
        self.le_data_description.clear()
        self.cmb_capture_method.setEnabled(1)
        self.cmb_capture_method.setCurrentIndex(0)
        self.cmb_organisation.setEnabled(1)
        self.cmb_organisation.setCurrentIndex(0)
        self.btn_bl_save.show()
        self.btn_bl_reset.show()

        self.current_dataset = None
        self.lb_dataset_id.setText('None')

        self.btn_compare_outlines.setDisabled(1)
        self.btn_alter_rel.setDisabled(1)
        self.btn_publish.setDisabled(1)

        self.add_historic_outlines()

        self.l_cs_area_title.setText('')

        iface.building_toolbar.hide()

    def display_data_exists(self):
        """
            Display setup when data has been bulk loaded
            - subfunction of: display_not_published &
              display_current_bl_not_compared
        """
        bulk_load.populate_bulk_comboboxes(self)
        bulk_load.load_current_fields(self)

        self.grpb_bulk_load.show()
        self.ml_outlines_layer.setDisabled(1)
        self.rad_external_id.setDisabled(1)
        self.fcb_external_id.setDisabled(1)
        self.cmb_capture_src_grp.setDisabled(1)
        self.cmb_cap_src_area.setDisabled(1)
        self.le_data_description.setDisabled(1)
        self.cmb_capture_method.setDisabled(1)
        self.cmb_organisation.setDisabled(1)
        self.btn_bl_save.hide()
        self.btn_bl_reset.hide()

        sql = reference_select.capture_source_area_name_by_supplied_dataset
        area_id = self.db._execute(sql, (self.current_dataset,))

        area_id = area_id.fetchall()
        if area_id is not None:
            self.l_cs_area_title.setText(area_id[0][0])
        else:
            self.l_cs_area_title.setText('')

    def display_not_published(self):
        """
            UI display when there is a dataset that hasn't been published.
        """
        self.display_data_exists()
        self.btn_compare_outlines.setDisabled(1)
        self.btn_publish.setEnabled(1)
        self.setup_toolbar()

    def display_current_bl_not_compared(self):
        """
            UI Display when there is a dataset that hasn't been compared.
        """

        self.display_data_exists()
        self.btn_compare_outlines.setEnabled(1)
        sql = reference_select.capture_source_area_name_by_supplied_dataset
        area_id = self.db._execute(sql, (self.current_dataset,))
        if area_id is not None:
            self.area_id = area_id.fetchall()
        if len(self.area_id) > 0:
            self.area_id = self.area_id[0][0]
            self.l_cs_area_title.setText(self.area_id)
        else:
            self.area_id = None
            self.l_cs_area_title.setText('')
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report(
                '\n ---------------------- NO CAPTURE SOURCE AREA ---------'
                '----------------- \n\nThere is no area id, please fix in database'
            )
            self.error_dialog.show()
            self.display_dataset_error()
            self.btn_compare_outlines.setDisabled(1)
            return
        self.btn_alter_rel.setDisabled(1)
        self.btn_publish.setDisabled(1)
        self.setup_toolbar()

    def add_outlines(self):
        """
            Add bulk load outlines of current dataset to canvas.
        """

        path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            'styles/')
        # add the bulk_load_outlines to the layer registry
        self.bulk_load_layer = self.layer_registry.add_postgres_layer(
            'bulk_load_outlines', 'bulk_load_outlines',
            'shape', 'buildings_bulk_load', '',
            'supplied_dataset_id = {0}'.format(self.current_dataset))
        self.bulk_load_layer.loadNamedStyle(path + 'building_editing.qml')
        iface.setActiveLayer(self.bulk_load_layer)

    def add_historic_outlines(self):
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            'styles/')
        self.historic_layer = self.layer_registry.add_postgres_layer(
            'loaded_datasets', 'bulk_load_outlines',
            'shape', 'buildings_bulk_load', '', '')
        self.historic_layer.loadNamedStyle(path + 'building_historic.qml')

    @pyqtSlot(int)
    def cmb_capture_src_grp_changed(self, index):
        self.cmb_cap_src_area.clear()
        id_capture_src_grp = self.ids_capture_src_grp[index]
        result = self.db._execute(common_select.capture_source_external_id_and_area_title_by_group_id, (id_capture_src_grp, ))
        ls = result.fetchall()
        for (external_id, area_title) in reversed(ls):
            text = external_id + '- ' + area_title
            self.cmb_cap_src_area.addItem(text)

    @pyqtSlot(bool)
    def cb_bulk_load_clicked(self, checked):
        layer_tree_layer = QgsProject.instance().layerTreeRoot().findLayer(self.bulk_load_layer.id())
        layer_tree_model = iface.layerTreeView().model()
        categories = layer_tree_model.layerLegendNodes(layer_tree_layer)
        bulk_category = [ln for ln in categories if ln.data(Qt.DisplayRole) == 'Bulk Loaded']
        if checked:
            bulk_category[0].setData(Qt.Checked, Qt.CheckStateRole)
        else:
            bulk_category[0].setData(Qt.Unchecked, Qt.CheckStateRole)

    @pyqtSlot(bool)
    def cb_added_clicked(self, checked):
        layer_tree_layer = QgsProject.instance().layerTreeRoot().findLayer(self.bulk_load_layer.id())
        layer_tree_model = iface.layerTreeView().model()
        categories = layer_tree_model.layerLegendNodes(layer_tree_layer)
        added_category = [ln for ln in categories if ln.data(Qt.DisplayRole) == 'Added During QA']
        added_edit_category = [ln for ln in categories if ln.data(Qt.DisplayRole) == 'Added- to be saved']
        if checked:
            added_category[0].setData(Qt.Checked, Qt.CheckStateRole)
            added_edit_category[0].setData(Qt.Checked, Qt.CheckStateRole)
        else:
            added_category[0].setData(Qt.Unchecked, Qt.CheckStateRole)
            added_edit_category[0].setData(Qt.Unchecked, Qt.CheckStateRole)

    @pyqtSlot(bool)
    def cb_removed_clicked(self, checked):
        layer_tree_layer = QgsProject.instance().layerTreeRoot().findLayer(self.bulk_load_layer.id())
        layer_tree_model = iface.layerTreeView().model()
        categories = layer_tree_model.layerLegendNodes(layer_tree_layer)
        removed_category = [ln for ln in categories if ln.data(Qt.DisplayRole) == 'Removed During QA']
        if checked:
            removed_category[0].setData(Qt.Checked, Qt.CheckStateRole)
        else:
            removed_category[0].setData(Qt.Unchecked, Qt.CheckStateRole)

    @pyqtSlot(bool)
    def bulk_load_save_clicked(self, commit_status):
        """
            When bulk load outlines save clicked
        """
        if self.confirm(self.msgbox_bulk_load):
            QApplication.setOverrideCursor(Qt.WaitCursor)
            bulk_load.bulk_load(self, commit_status)
            # find if adding was sucessful
            result = self.db._execute(bulk_load_select.supplied_dataset_count_both_dates_are_null)
            result = result.fetchall()[0][0]
            # if bulk loading completed without errors
            if result == 1:
                QgsMapLayerRegistry.instance().layerWillBeRemoved.disconnect(self.layers_removed)
                self.layer_registry.remove_layer(self.historic_layer)
                QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.layers_removed)
                self.cmb_capture_src_grp.currentIndexChanged.disconnect(self.cmb_capture_src_grp_changed)
                self.add_outlines()
                self.display_current_bl_not_compared()
            QApplication.restoreOverrideCursor()
            self.edit_dialog = EditDialog(self)

    @pyqtSlot()
    def bulk_load_reset_clicked(self):
        """
            When bulk Load reset clicked
        """
        self.cmb_capture_method.setCurrentIndex(0)
        self.ml_outlines_layer.setCurrentIndex(0)
        self.cmb_organisation.setCurrentIndex(0)
        self.le_data_description.clear()
        self.rad_external_id.setChecked(False)

    @pyqtSlot(bool)
    def compare_outlines_clicked(self, commit_status):
        """
            When compare outlines clicked
        """
        if self.confirm(self.msgbox_compare):
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.edit_cancel_clicked()
            comparisons.compare_outlines(self, commit_status)
            self.btn_publish.setEnabled(1)
            self.btn_compare_outlines.setDisabled(1)
            self.btn_alter_rel.setEnabled(1)
            QApplication.restoreOverrideCursor()

    def canvas_add_outline(self):
        """
            When add outline radio button toggled
        """
        self.edit_dialog.add_outline()
        self.edit_dialog.show()
        self.change_instance = self.edit_dialog.get_change_instance()

        self.circle_tool = None
        self.polyline = None
        # setup circle button
        image_dir = os.path.join(__location__, '..', 'icons')
        icon_path = os.path.join(image_dir, "circle.png")
        icon = QIcon()
        icon.addFile(icon_path, QSize(8, 8))
        self.circle_action = QAction(icon, "Draw Circle", iface.building_toolbar)
        iface.registerMainWindowAction(self.circle_action, "Ctrl+0")
        self.circle_action.triggered.connect(self.setup_circle)
        self.circle_action.setCheckable(True)
        iface.building_toolbar.addAction(self.circle_action)

    def canvas_edit_attribute(self):
        """
            When edit outline radio button toggled
        """
        self.edit_dialog.show()
        self.edit_dialog.edit_attribute()
        self.change_instance = self.edit_dialog.get_change_instance()

    def canvas_edit_geometry(self):
        """
            When edit geometry radio button toggled
        """
        self.edit_dialog.edit_geometry()
        self.edit_dialog.show()
        self.change_instance = self.edit_dialog.get_change_instance()

    def edit_cancel_clicked(self):
        """
            When cancel clicked
        """
        if len(QgsMapLayerRegistry.instance().mapLayersByName('bulk_load_outlines')) > 0:
            if isinstance(self.change_instance, bulk_load_changes.EditAttribute):
                try:
                    self.bulk_load_layer.selectionChanged.disconnect(self.change_instance.selection_changed)
                except TypeError:
                    pass
            elif isinstance(self.change_instance, bulk_load_changes.EditGeometry):
                try:
                    self.bulk_load_layer.geometryChanged.disconnect()
                except TypeError:
                    pass
            elif isinstance(self.change_instance, bulk_load_changes.AddBulkLoad):
                try:
                    self.bulk_load_layer.featureAdded.disconnect()
                except TypeError:
                    pass
                try:
                    self.bulk_load_layer.featureDeleted.disconnect()
                except TypeError:
                    pass
                try:
                    self.bulk_load_layer.geometryChanged.disconnect()
                except TypeError:
                    pass
                if self.polyline:
                    self.polyline.reset()
                if isinstance(self.circle_tool, PointTool):
                    self.circle_tool.canvas_clicked.disconnect()
                    self.circle_tool.mouse_moved.disconnect()
                    self.circle_tool.deactivate()
                iface.actionPan().trigger()

        iface.actionCancelEdits().trigger()

        QgsMapLayerRegistry.instance().layerWillBeRemoved.disconnect(self.layers_removed)
        self.edit_dialog.remove_territorial_auth()
        QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.layers_removed)

        self.setup_toolbar()

        self.change_instance = None

    @pyqtSlot()
    def setup_circle(self):
        """
            called when draw circle button is clicked
        """
        self.points = []
        # set map tool to new point tool
        self.circle_tool = PointTool(iface.mapCanvas())
        iface.mapCanvas().setMapTool(self.circle_tool)
        # create polyline to track drawing on canvas
        self.polyline = QgsRubberBand(iface.mapCanvas(), False)
        self.polyline.setLineStyle(Qt.PenStyle(Qt.DotLine))
        self.polyline.setColor(QColor(255, 0, 0))
        self.polyline.setWidth(1)
        # signals for new map tool
        self.circle_tool.canvas_clicked.connect(self.draw_circle)
        self.circle_tool.mouse_moved.connect(self.update_line)

    @pyqtSlot(QgsPoint)
    def draw_circle(self, point):
        """
            called when mapcanvas is clicked
        """
        self.points.append(point)
        self.polyline.addPoint(point, True)
        self.polyline.setToGeometry(QgsGeometry.fromPolyline(self.points), None)
        # if two points have been clicked (center and edge)
        if len(self.points) == 2:
            # calculate radius of circle
            radius = math.sqrt((self.points[1][0] - self.points[0][0])**2 + (self.points[1][1] - self.points[0][1])**2)
            # number of vertices of circle
            nodes = (round(math.pi / math.acos((radius - 0.001) / radius))) / 10
            # create point on center location
            point = QgsGeometry.fromPoint(QgsPoint(self.points[0]))
            # create buffer of specified distance around point
            buffer = point.buffer(radius, nodes)
            # add feature to bulk_load_outlines (triggering featureAdded)
            self.feature = QgsFeature(self.bulk_load_layer.pendingFields())
            self.feature.setGeometry(buffer)
            self.bulk_load_layer.addFeature(self.feature)
            self.bulk_load_layer.triggerRepaint()
            # reset points list
            self.points = []

    @pyqtSlot(QgsPoint)
    def update_line(self, point):
        """
            called when mouse moved on canvas
        """
        if len(self.points) == 1:
            # if the center has been clicked have a line follow the mouse movement
            line = [self.points[0], point]
            self.polyline.setToGeometry(QgsGeometry.fromPolyline(line), None)

    @pyqtSlot()
    def alter_relationships_clicked(self):
        """
            When alter relationships button clicked
            open alter relationships frame
        """
        if self.change_instance is not None:
            self.edit_dialog.close()
        self.db.close_connection()
        QgsMapLayerRegistry.instance().layerWillBeRemoved.disconnect(self.layers_removed)
        self.layer_registry.remove_layer(self.bulk_load_layer)
        dw = self.dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(AlterRelationships(
            dw, self.current_dataset))
        for action in iface.building_toolbar.actions():
            if action.objectName() not in ['mActionPan']:
                iface.building_toolbar.removeAction(action)
        iface.building_toolbar.hide()

    @pyqtSlot(bool)
    def publish_clicked(self, commit_status):
        """
            When publish button clicked
        """
        if not self.check_duplicate_ids():
            return
        if self.confirm(self.msgbox_publish):
            QApplication.setOverrideCursor(Qt.WaitCursor)
            if self.change_instance is not None:
                self.edit_dialog.close()
            self.db.open_cursor()
            sql = 'SELECT buildings_bulk_load.load_building_outlines(%s);'
            self.db.execute_no_commit(sql, (self.current_dataset,))
            if commit_status:
                self.db.commit_open_cursor()
            self.display_no_bulk_load()
            self.cmb_capture_src_grp.currentIndexChanged.connect(self.cmb_capture_src_grp_changed)
            self.current_dataset = None
            self.lb_dataset_id.setText('None')
            QgsMapLayerRegistry.instance().layerWillBeRemoved.disconnect(self.layers_removed)
            self.layer_registry.remove_layer(self.bulk_load_layer)
            self.add_historic_outlines()
            QApplication.restoreOverrideCursor()
            self.grpb_layers.hide()
            QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.layers_removed)

    def check_duplicate_ids(self):
        """
            Check same ids in different tables (added/matched/related)
        """
        result = self.run_check()
        if not result:
            return True
        else:
            self.check_dialog.show()
            self.check_dialog.set_message('FAILED: duplicate id(s) found.')
            self.check_dialog.set_data(result)
            return False

    def run_check(self):
        """
            Run check and return the output data
        """
        result = self.db._execute(bulk_load_select.added_outlines_by_dataset_id, (self.current_dataset,))
        added_outlines = result.fetchall()
        result = self.db._execute(bulk_load_select.matched_outlines_by_dataset_id, (self.current_dataset,))
        matched_outlines = result.fetchall()
        result = self.db._execute(bulk_load_select.related_outlines_by_dataset_id, (self.current_dataset,))
        related_outlines = result.fetchall()
        ids_added_matched = self.find_match_ids(added_outlines, matched_outlines)
        ids_added_related = self.find_match_ids(added_outlines, related_outlines)
        ids_matched_related = self.find_match_ids(matched_outlines, related_outlines)
        data = self.get_error_data(ids_added_matched, ids_added_related, ids_matched_related)
        return data

    def find_match_ids(self, ids_1, ids_2):
        return list(set(ids_1) & set(ids_2))

    def get_error_data(self, ids_added_matched, ids_added_related, ids_matched_related):
        """
            Return the output data
        """
        data = []
        for (feat_id,) in ids_added_matched:
            data.append((feat_id, 'Added', 'Matched'))
        for (feat_id,) in ids_added_related:
            data.append((feat_id, 'Added', 'Related'))
        for (feat_id,) in ids_matched_related:
            data.append((feat_id, 'Matched', 'Related'))
        return data

    @pyqtSlot()
    def exit_clicked(self):
        """
            Called when bulk load frame exit button clicked.
        """
        self.close_frame()
        self.dockwidget.lst_sub_menu.clearSelection()

    def close_frame(self):
        """
            Clean up and remove the bulk load frame.
        """
        if self.change_instance is not None:
            self.edit_dialog.close()
        QgsMapLayerRegistry.instance().layerWillBeRemoved.disconnect(self.layers_removed)
        iface.actionCancelEdits().trigger()
        if self.historic_layer is not None:
            self.layer_registry.remove_layer(self.historic_layer)
        if self.bulk_load_layer is not None:
            self.layer_registry.remove_layer(self.bulk_load_layer)
        if self.territorial_auth is not None:
            self.layer_registry.remove_layer(self.territorial_auth)
        from buildings.gui.menu_frame import MenuFrame
        dw = self.dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(MenuFrame(dw))
        for action in iface.building_toolbar.actions():
            if action.text() not in ['Pan Map']:
                iface.building_toolbar.removeAction(action)
        iface.building_toolbar.hide()

    @pyqtSlot(str)
    def layers_removed(self, layerids):
        self.layer_registry.update_layers()
        if 'bulk_load_outlines' in layerids or 'territorial_authorities' in layerids:
            self.btn_compare_outlines.setDisabled(1)
            self.btn_alter_rel.setDisabled(1)
            self.btn_publish.setDisabled(1)
            self.cb_bulk_load.setDisabled(1)
            self.cb_added.setDisabled(1)
            self.cb_removed.setDisabled(1)
            for action in iface.building_toolbar.actions():
                if action.text() not in ['Pan Map', 'Add Outline', 'Edit Geometry', 'Edit Attributes']:
                    iface.building_toolbar.removeAction(action)
                if action.text() in ['Add Outline', 'Edit Geometry', 'Edit Attributes']:
                    action.setDisabled(True)
                else:
                    action.setEnabled(True)
            iface.messageBar().pushMessage("ERROR",
                                           "Required layer Removed! Please reload the buildings plugin or the current frame before continuing",
                                           level=QgsMessageBar.CRITICAL, duration=5)
            return

        if 'loaded_datasets' in layerids:
            iface.messageBar().pushMessage("ERROR",
                                           "Required layer Removed! Please reload the buildings plugin or the current frame before continuing",
                                           level=QgsMessageBar.CRITICAL, duration=5)
            # disable bulk loading buttons
            self.btn_bl_save.setDisabled(1)
            self.btn_bl_reset.setDisabled(1)
            return
