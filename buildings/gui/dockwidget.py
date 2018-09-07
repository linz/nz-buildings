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

from PyQt4.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt4.QtGui import QDockWidget, QListWidgetItem
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

        # Change look of options list widget
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

        # Change look of sub menu list widget
        self.lst_sub_menu.setStyleSheet(
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

        self.lst_sub_menu.itemClicked.connect(self.show_frame)

    @pyqtSlot(QListWidgetItem)
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

    @pyqtSlot(QListWidgetItem)
    def show_frame(self, item):
        if item:
            print item.text()
            from buildings.utilities.layers import LayerRegistry
            from buildings.utilities import database as db
            db.close_connection()
            layer_registry = LayerRegistry()
            self.stk_options.removeWidget(self.stk_options.currentWidget())
            if item.text() == 'Capture Sources':
                from buildings.gui.new_capture_source import NewCaptureSource
                self.new_widget(NewCaptureSource(self, layer_registry))
            elif item.text() == 'Bulk Load':
                from buildings.gui.bulk_load_frame import BulkLoadFrame
                self.new_widget(BulkLoadFrame(self, layer_registry))
            elif item.text() == 'Edit Outlines':
                from buildings.gui.production_frame import ProductionFrame
                self.new_widget(ProductionFrame(self, layer_registry))
            elif item.text() == 'Settings':
                from buildings.gui.new_entry import NewEntry
                self.new_widget(NewEntry(self, layer_registry))

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

        return """
            QTabWidget::pane {
                /* The tab widget frame */
                border-top: 2px solid #C2C7CB;
            }
            QTabWidget::tab-bar {
                /* move to the right by 5px */
                left: 5px;
            }

            QTabBar::tab {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #E1E1E1,
                    stop: 0.4 #e7e7e7, stop: 0.5 #e7e7e7, stop: 1.0 #D3D3D3
                );
                border: 2px solid #C4C4C3;
                border-bottom-color: #C2C7CB;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 3px;
            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ececec,
                    stop: 0.4 #f4f4f4, stop: 0.5 #e7e7e7, stop: 1.0 #ececec
                );
            }
            QTabBar::tab:selected {
                border-color: #9B9B9B;
                border-bottom-color: #f0f0f0; /* same as pane color */
            }
            QTabBar::tab:!selected {
                /* make non-selected tabs look smaller */
                margin-top: 2px;
            }
            QTabBar::tab:selected {
                /* expand to the left and right by 4px */
                margin-left: 0px;
                margin-right: 0px;
            }
            QTabBar::tab:first:selected {
                /* the first selected tab has nothing to overlap with on the left */
                margin-left: 0;
            }
            QTabBar::tab:last:selected {
                /* the last selected tab has nothing to overlap with on the right */
                margin-right: 0;
            }
            QTabBar::tab:only-one {
                /* if there is only one tab, we don't want overlapping margins */
                margin: 1;
            }
        """

    def focusInEvent(self, event):
        self.in_focus.emit()
