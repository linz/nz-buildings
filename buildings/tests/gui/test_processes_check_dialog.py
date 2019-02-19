# -*- coding: utf-8 -*-
"""
################################################################################
#
# Copyright 2018 Crown copyright (c)
# Land Information New Zealand and the New Zealand Government.
# All rights reserved
#
# This program is released under the terms of the 3 clause BSD license. See the
# LICENSE file for more information.
#
################################################################################

    Tests: Check dialog on publish Processes

 ***************************************************************************/
"""

import os
import unittest

from PyQt4.QtGui import QStandardItem, QStandardItemModel

from buildings.gui.check_dialog import CheckDialog


class ProcessesCheckDialog(unittest.TestCase):
    """
    Test check dialog process
    """
    @classmethod
    def setUpClass(cls):
        """Runs at TestCase init."""
        cls.check_dialog = CheckDialog()

    @classmethod
    def tearDownClass(cls):
        """Runs at TestCase teardown."""
        pass

    def setUp(self):
        """Runs before each test."""
        self.check_dialog.show()

    def tearDown(self):
        """Runs after each test."""
        self.check_dialog.close()
        if os.path.isfile(self.output_file):
            os.remove(self.output_file)

    def test_btn_export_clicked(self):
        """Check file exported to the directory when bth_export clicked"""
        model = QStandardItemModel(1, 3)
        model.setHorizontalHeaderItem(0, QStandardItem('Duplicate Id'))
        model.setHorizontalHeaderItem(1, QStandardItem('Table'))
        model.setHorizontalHeaderItem(2, QStandardItem('Table'))
        model.setData(model.index(0, 0), '2003')
        model.setData(model.index(0, 1), 'Added')
        model.setData(model.index(0, 2), 'Matched')
        self.check_dialog.tbl_dup_ids.setModel(model)
        save_path = os.path.expanduser('~')
        save_filename = 'Test_duplicate_check_output'
        self.check_dialog.le_path.setText(save_path)
        self.check_dialog.le_filename.setText(save_filename)
        self.check_dialog.btn_export.click()
        self.output_file = os.path.join(save_path, save_filename)
        self.assertTrue(os.path.isfile(self.output_file))
