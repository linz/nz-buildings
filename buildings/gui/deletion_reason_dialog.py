import os

from PyQt4 import uic
from PyQt4.QtGui import QDialog
from PyQt4.QtCore import Qt

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'deletion_reason.ui'))


class DeletionReason(QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        super(DeletionReason, self).__init__(parent)
        self.setupUi(self)
        self.setWindowModality(Qt.ApplicationModal)
