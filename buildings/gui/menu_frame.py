# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtGui import QFrame, QPixmap


# Get the path for the parent directory of this file.
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'menu_frame.ui'))


class MenuFrame(QFrame, FORM_CLASS):

    def __init__(self, dockwidget, layer_registry, parent=None):
        """Constructor."""
        super(MenuFrame, self).__init__(parent)
        self.setupUi(self)

        self.txt_dashboard.viewport().setAutoFillBackground(False)
