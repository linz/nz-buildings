# -*- coding: utf-8 -*-
"""
################################################################################
#
# Copyright 2016 Crown copyright (c)
# Land Information New Zealand and the New Zealand Government.
# All rights reserved
#
# This program is released under the terms of the 3 clause BSD license. See the
# LICENSE file for more information.
#
################################################################################

    This script deals with styles and enabling statuses of objects in the
    main ui on prompts.

 ***************************************************************************/
"""

import os

from PyQt4.QtCore import Qt, pyqtSignal, QSize, pyqtSlot, QDate, QSignalMapper
from PyQt4.QtGui import QDockWidget, QPixmap, QIcon, QListWidgetItem, QMenu, QAction, QCursor
from PyQt4 import uic

from buildings.settings.project import set_crs
from buildings.settings import project

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dockwidget_base.ui'))


class BuildingsDockwidget(QDockWidget, FORM_CLASS):
    closed = pyqtSignal()
    in_focus = pyqtSignal()

    frames = {}
    current_frame = None

    def __init__(self, parent=None):
        """Constructor."""
        super(BuildingsDockwidget, self).__init__(parent)

        # Set up the user interface from Designer.
        self.setupUi(self)

        # Set focus policy so can track when user clicks back onto dock widget
        self.setFocusPolicy(Qt.StrongFocus)

        # Change look of list widget
        self.lst_options.setStyleSheet(
            """ QListWidget {
                    background-color: rgb(69, 69, 69, 0);
                    outline: 0;
                }
                QListWidget::item {
                    color: white;
                    padding: 3px;
                }
                QListWidget::item::selected {
                    color: black;
                    background-color:palette(Window);
                    padding-right: 0px;
                };
            """
        )

        self.frm_options.setStyleSheet(
            """ QFrame {
                    background-color: rgb(69, 69, 69, 220);
                };
            """
        )

        # Signals for clicking on lst_options
        self.lst_options.itemClicked.connect(self.show_selected_option)
        self.lst_options.itemClicked.emit(self.lst_options.item(0))

    def show_selected_option(self, item):
        if item:
            if item.text() == 'Buildings':
                project.SRID = 2193
                set_crs()
                if self.stk_options.count() == 2:
                    self.stk_options.setCurrentIndex(0)
                    self.stk_options.addWidget(self.frames['menu_frame'])
                    self.current_frame = self.frames['menu_frame']
                    self.stk_options.setCurrentIndex(1)
                else:
                    self.stk_options.setCurrentIndex(1)

    def new_widget(self, frame):
        self.stk_options.addWidget(frame)
        self.stk_options.setCurrentIndex(1)
        self.current_frame = frame

    # insert into dictionary
    def insert_into_frames(self, text, object):
        self.frames[text] = object

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()

    def defaultStyle(self):
        """default tab Widget style"""
        return """QTabWidget::pane { /* The tab widget frame */border-top: 2px solid #C2C7CB;}
            QTabWidget::tab-bar {left: 5px; /* move to the right by 5px */}

            QTabBar::tab {background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #E1E1E1, stop: 0.4 #e7e7e7,
                                                    stop: 0.5 #e7e7e7, stop: 1.0 #D3D3D3);
                            border: 2px solid #C4C4C3;border-bottom-color: #C2C7CB;
                            border-top-left-radius: 4px;border-top-right-radius: 4px;padding: 3px;}

            QTabBar::tab:selected, QTabBar::tab:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #ececec, stop: 0.4 #f4f4f4,
                                            stop: 0.5 #e7e7e7, stop: 1.0 #ececec);}
            QTabBar::tab:selected {
                border-color: #9B9B9B;border-bottom-color: #f0f0f0; /* same as pane color */}

            QTabBar::tab:!selected {
                margin-top: 2px; /* make non-selected tabs look smaller */}

            QTabBar::tab:selected {/* expand/overlap to the left and right by 4px */
                margin-left: 0px;margin-right: 0px;}/* make use of negative margins for overlapping tabs */

            QTabBar::tab:first:selected {
                margin-left: 0; /* the first selected tab has nothing to overlap with on the left */}

            QTabBar::tab:last:selected {
                margin-right: 0; /* the last selected tab has nothing to overlap with on the right */}

            QTabBar::tab:only-one {
                margin: 1; /* if there is only one tab, we don't want overlapping margins */} """

    def focusInEvent(self, event):
        self.in_focus.emit()
