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

    Tests: Menu GUI Processes

 ***************************************************************************/
"""

import unittest
from qgis.utils import plugins
from qgis.utils import reloadPlugin

class ProcessMenuGuiTest(unittest.TestCase):
    """Test Menu GUI Processes"""
    @classmethod
    def setUpClass(cls):
        """Runs at TestCase init."""
        if not plugins.get('roads'):
            pass
        else:
            cls.road_plugin = plugins.get('roads')
            if cls.road_plugin.is_active is False:
                cls.road_plugin.main_toolbar.actions()[0].trigger()
                cls.dockwidget = cls.road_plugin.dockwidget
            else:
                cls.dockwidget = cls.road_plugin.dockwidget
            if not plugins.get('buildings'):
                pass
            else:
                cls.building_plugin = plugins.get('buildings')
                reloadPlugin('buildings')
                if cls.dockwidget.stk_options.count() == 4:
                    cls.dockwidget.stk_options.setCurrentIndex(3)
                    cls.dockwidget.stk_options.addWidget(cls.dockwidget.frames['menu_frame'])
                    cls.dockwidget.current_frame = 'menu_frame'
                    cls.dockwidget.stk_options.setCurrentIndex(4)
                else:
                    cls.dockwidget.stk_options.setCurrentIndex(4)
                cls.dockwidget.lst_options.setCurrentItem(cls.dockwidget.lst_options.item(2))

    @classmethod
    def tearDownClass(cls):
        """Runs at TestCase teardown."""
        cls.road_plugin.dockwidget.close()

    def setUp(self):
        self.road_plugin = plugins.get('roads')
        self.building_plugin = plugins.get('buildings')
        self.road_plugin.main_toolbar.actions()[0].trigger()
        self.dockwidget = self.road_plugin.dockwidget
        self.menu_frame = self.building_plugin.menu_frame

    def tearDown(self):
        """Runs after each test"""
        # Do nothing

    def test_new_entry_on_click(self):
        # new entry
        self.menu_frame.btn_new_entry.click()
        self.assertEqual(self.dockwidget.current_frame.objectName(), 'f_new_entry')
        self.dockwidget.current_frame.btn_cancel.click()
    
    def test_new_capture_source_on_click(self):
        # new capture source
        self.menu_frame.btn_add_capture_source.click()
        self.assertEqual(self.dockwidget.current_frame.objectName(), 'f_new_capture_source')
        self.dockwidget.current_frame.btn_cancel.click()
        
    def test_bulk_load_outlines_on_click(self):
        # Bulk load outlines
        self.menu_frame.btn_load_outlines.click()
        self.assertEqual(self.dockwidget.current_frame.objectName(), 'f_new_supplied_outlines')
        self.dockwidget.current_frame.btn_cancel.click()
        
    def test_cmb_bulk_create_outlines_on_click(self):
        # Bulk create outline
        self.menu_frame.cmb_add_outline.setCurrentIndex(1)
        self.assertEqual(self.dockwidget.current_frame.objectName(), 'f_bulk_new_outline')
        self.dockwidget.current_frame.error_dialog.close()
        self.dockwidget.current_frame.btn_cancel.click()
    
    def test_cmb_production_create_outlines_on_click(self):
        self.menu_frame.cmb_add_outline.setCurrentIndex(2)
        self.assertEqual(self.dockwidget.current_frame.objectName(), 'f_production_new_outline')
        self.dockwidget.current_frame.btn_cancel.click()


suite = unittest.TestLoader().loadTestsFromTestCase(ProcessMenuGuiTest)
unittest.TextTestRunner(verbosity=2).run(suite)

