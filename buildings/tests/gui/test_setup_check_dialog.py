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

    Tests: Check dialog on publish setup confirm default settings

 ***************************************************************************/
"""

import unittest

from buildings.gui.check_dialog import CheckDialog


class SetUpCheckDialog(unittest.TestCase):
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

    def test_check_dialog_gui_set_up(self):
        """ Initial set up of the dialog """
        self.assertEqual(self.check_dialog.tbl_dup_ids.model(), None)
        self.assertTrue(self.check_dialog.btn_browse.isEnabled())
        self.assertFalse(self.check_dialog.btn_export.isEnabled())
        self.assertEqual(self.check_dialog.le_path.text(), "")
        self.assertNotEqual(self.check_dialog.le_filename.text(), "")
