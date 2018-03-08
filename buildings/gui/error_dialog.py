import os
from PyQt4 import uic
from PyQt4.QtGui import QDialog, QPixmap
from PyQt4.QtCore import pyqtSignal, Qt
from qgis.utils import QGis

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "error_dialog.ui"))

class ErrorDialog(QDialog, FORM_CLASS):

    closingDialog = pyqtSignal()

    def __init__(self, parent=None):
        super(ErrorDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowModality(Qt.ApplicationModal)

    def fill_report(self, txt):
        self.tb_error_report.setText(txt)
        if self.tb_error_report.toPlainText():
            return True
        else:
            return False
