import os

from PyQt4 import uic
from PyQt4.QtGui import QCompleter, QDialog
from PyQt4.QtCore import Qt

from buildings.sql import buildings_bulk_load_select_statements as bulk_load_select
from buildings.utilities import database as db

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'deletion_reason.ui'))


class DeletionReason(QDialog, FORM_CLASS):

    def __init__(self, selected_number, parent=None):
        super(DeletionReason, self).__init__(parent)
        self.setupUi(self)
        self.setWindowModality(Qt.ApplicationModal)
        self.db = db
        # initiate label
        self.lb_reason.setText("Number of outlines that will be deleted: {}".format(selected_number))
        # initiate le_deletion_reason
        self.le_reason.setMaxLength(250)
        self.le_reason.setPlaceholderText('Reason for Deletion')
        self.completer_box()

    def completer_box(self):
        """Box automatic completion"""
        reasons = self.db._execute(bulk_load_select.deletion_description_value)
        reason_list = [row[0] for row in reasons.fetchall()]
        # Fill the search box
        self.completer = QCompleter(reason_list)
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.le_reason.setCompleter(self.completer)
