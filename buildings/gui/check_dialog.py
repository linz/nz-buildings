import csv
import os

from PyQt4 import uic
from PyQt4.QtGui import (QAbstractItemView, QDialog, QFileDialog,
                         QHeaderView, QIcon, QStandardItem,
                         QStandardItemModel)
from PyQt4.QtCore import Qt, pyqtSlot

from qgis.core import QgsProject
from qgis.gui import QgsMessageBar
from qgis.utils import iface

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'check_dialog.ui'))


class CheckDialog(QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        super(CheckDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowModality(Qt.ApplicationModal)

        self.init_table()
        self.btn_export.setDisabled(True)
        self.le_filename.setText('duplicate_ids_check')

        self.btn_browse.setIcon(QIcon(os.path.join(__location__, '..', 'icons', 'browse.png')))
        self.btn_browse.clicked.connect(self.open_browse)
        self.le_path.textChanged.connect(self.le_path_text_changed)
        self.le_filename.textChanged.connect(self.le_filename_text_changed)
        self.btn_export.clicked.connect(self.export)

    def init_table(self):
        """Initialise the table"""
        self.tbl_dup_ids.verticalHeader().hide()
        self.tbl_dup_ids.horizontalHeader().setResizeMode(QHeaderView.Stretch)

    @pyqtSlot()
    def open_browse(self):
        """Browses the user's directory."""
        save_path = QgsProject.instance().fileName()    # Get current project's path
        if not save_path:
            save_path = os.path.expanduser('~')         # Get user's home path

        out_path = QFileDialog.getExistingDirectory(
            self,
            'Select Output Directory',
            save_path,
            QFileDialog.ShowDirsOnly)
        self.le_path.setText(out_path)
        path_status = self.check_path()
        name_status = self.check_file_name()
        self.btn_export.setEnabled(path_status & name_status)

    @pyqtSlot()
    def le_path_text_changed(self):
        path_status = self.check_path()
        name_status = self.check_file_name()
        self.btn_export.setEnabled(path_status & name_status)

    @pyqtSlot()
    def le_filename_text_changed(self):
        path_status = self.check_path()
        name_status = self.check_file_name()
        self.btn_export.setEnabled(path_status & name_status)

    @pyqtSlot()
    def export(self):
        """Exports as csv"""
        csv_name = self.le_filename.text()
        csv_path = os.path.join(self.le_path.text(), csv_name)

        if os.path.isfile(csv_path):
            iface.messageBar().pushMessage(
                'Failed to export csv', '{} already existed.'.format(csv_path), level=QgsMessageBar.CRITICAL)
        else:
            with open(csv_path, 'wb') as csv_file:
                writer = csv.writer(csv_file)
                # Add headers
                header = []
                tbl = self.tbl_dup_ids
                tbl_model = tbl.model()
                for col in range(tbl_model.columnCount()):
                    header.append(str(tbl_model.horizontalHeaderItem(col).text()))
                writer.writerow(header)
                # Add contents
                for row in range(tbl_model.rowCount()):
                    row_data = []
                    for col in range(tbl_model.columnCount()):
                        item = tbl_model.item(row, col)
                        row_data.append(item.text())
                    writer.writerow(row_data)
            iface.messageBar().pushMessage(
                'Saved', 'Error Output has been saved to {}'.format(csv_path), level=QgsMessageBar.SUCCESS)

    def check_path(self):
        """Check if path is valid"""
        warn_msg = []
        ok_status = True
        out_path = self.le_path.text()
        if not out_path or out_path.isspace():
            ok_status = False
        elif not os.path.isdir(out_path):
            ok_status = False
            warn_msg.append('Output directory does not exist')
        if out_path:
            if out_path[-1] == '/' or out_path[-1] == '\\':
                ok_status = False
                warn_msg.append('Directory cannot end with / or \\ ')
        self.l_path_error.setText(', '.join(warn_msg))
        return ok_status

    def check_file_name(self):
        """Check if file name is valid"""
        if self.le_filename.text() == '':
            return False
        return True

    def set_message(self, message):
        """Update the message"""
        self.l_check_status.setText(message)

    def set_data(self, data):
        """Update the table data"""
        model = QStandardItemModel(len(data), 3)
        model.setHorizontalHeaderItem(0, QStandardItem('Duplicate Id'))
        model.setHorizontalHeaderItem(1, QStandardItem('Table'))
        model.setHorizontalHeaderItem(2, QStandardItem('Table'))
        row = 0
        for (feat_id, rel1, rel2) in data:
            model.setData(model.index(row, 0), str(feat_id))
            model.setData(model.index(row, 1), rel1)
            model.setData(model.index(row, 2), rel2)
            row += 1
        self.tbl_dup_ids.setModel(model)
        self.tbl_dup_ids.setEditTriggers(QAbstractItemView.NoEditTriggers)
