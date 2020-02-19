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

    Tests: Reference Data GUI setup confirm default settings

 ***************************************************************************/
"""

import unittest

from qgis.PyQt.QtCore import Qt, QTimer
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.utils import plugins

from buildings.utilities import database as db


class SetUpReferenceData(unittest.TestCase):
    """Test Reference Data GUI initial setup confirm default settings"""

    def setUp(self):
        """Runs before each test."""
        self.building_plugin = plugins.get("buildings")
        self.building_plugin.main_toolbar.actions()[0].trigger()
        self.dockwidget = self.building_plugin.dockwidget
        sub_menu = self.dockwidget.lst_sub_menu
        sub_menu.setCurrentItem(sub_menu.findItems("Reference Data", Qt.MatchExactly)[0])
        self.reference_frame = self.dockwidget.current_frame

    def tearDown(self):
        """Runs after each test."""
        self.reference_frame.db.rollback_open_cursor()
        self.reference_frame.btn_exit.click()

    def test_suburb_locality_table_update(self):
        """Check buildings_reference.suburb_locality table updates correctly."""
        # insert building outline to check for deleted suburb id
        if self.reference_frame.db._open_cursor is None:
            self.reference_frame.db.open_cursor()
        insert_building = "SELECT buildings.buildings_insert();"
        insert_building_outline = "SELECT buildings.building_outlines_insert(%s, %s, %s, %s, %s, %s, %s, %s);"
        result = self.reference_frame.db.execute_no_commit(insert_building)
        building_id = result.fetchone()[0]
        result = self.reference_frame.db.execute_no_commit(
            insert_building_outline,
            (
                building_id,
                11,
                1002,
                1,
                101,
                1002,
                10002,
                "010300002091080000010000000500000054A0D29477AA3C4194E310ED71315541D10AA5B679AA3C415417E8DD643155410DA2D440E3AA3C4104CAAD99643155414BD7BD51E4AA3C4171B36E867331554154A0D29477AA3C4194E310ED71315541",
            ),
        )
        building_outline_id = result.fetchone()[0]

        # run reference update
        self.reference_frame.chbx_suburbs.setChecked(True)

        btn_ok = self.reference_frame.msgbox.button(QMessageBox.Ok)
        QTimer.singleShot(500, btn_ok.click)

        self.reference_frame.update_clicked(commit_status=False)

        # deleted suburb locality
        sql_removed = (
            "SELECT count(*)::integer FROM buildings_reference.suburb_locality WHERE external_suburb_locality_id = 104;"
        )
        result = db._execute(sql_removed)
        count_removed = result.fetchone()[0]
        self.assertEqual(count_removed, 0)
        sql_building_in_removed_area = (
            "SELECT suburb_locality_id from buildings.building_outlines WHERE building_outline_id = %s;"
        )
        result = db._execute(sql_building_in_removed_area, (building_outline_id,))
        suburb_id_of_removed_building = result.fetchone()[0]
        self.assertEqual(suburb_id_of_removed_building, 101)

        # new suburb locality
        sql_added = (
            "SELECT count(*)::integer FROM buildings_reference.suburb_locality WHERE external_suburb_locality_id = 105;"
        )
        result = db._execute(sql_added)
        count_added = result.fetchone()[0]
        self.assertEqual(count_added, 1)
        # updated suburb locality
        sql_updated = "SELECT suburb_4th FROM buildings_reference.suburb_locality WHERE external_suburb_locality_id = 101;"
        result = db._execute(sql_updated)
        name_updated = result.fetchone()[0]
        self.assertEqual(name_updated, "Kelburn North")
        # check last modified date
        sql_date = "SELECT last_modified FROM buildings.building_outlines WHERE building_outline_id = 1021;"
        modified_date = db._execute(sql_date)
        modified_date = result.fetchone()[0]
        self.assertNotEqual(modified_date, "NULL")
        sql_date = "SELECT last_modified FROM buildings.building_outlines WHERE building_outline_id = 1022;"
        modified_date = db._execute(sql_date)
        modified_date = result.fetchone()[0]
        self.assertIsNone(modified_date)
        # check building_outlines
        sql_bo = "SELECT count(DISTINCT suburb_locality_id)::integer FROM buildings.building_outlines;"
        result = db._execute(sql_bo)
        bo_suburb_update = result.fetchone()[0]
        self.assertEqual(bo_suburb_update, 4)
        sql_select_building_in_changed_region = (
            "SELECT suburb_locality_id FROM buildings.building_outlines WHERE building_outline_id = 1005;"
        )
        result = db._execute(sql_select_building_in_changed_region)
        suburb_id_bo_in_changed_region = result.fetchone()[0]
        self.assertEqual(suburb_id_bo_in_changed_region, 103)
        # check suburb locality only adds types locality, suburb, island, park_reserve
        sql_added = (
            "SELECT count(*)::integer FROM buildings_reference.suburb_locality WHERE external_suburb_locality_id = 106;"
        )
        result = db._execute(sql_added)
        count_added = result.fetchone()[0]
        self.assertEqual(count_added, 0)
        # check suburb locality island with null suburb_4th is added
        sql_added = (
            "SELECT count(*)::integer FROM buildings_reference.suburb_locality WHERE external_suburb_locality_id = 108;"
        )
        result = db._execute(sql_added)
        count_added = result.fetchone()[0]
        self.assertEqual(count_added, 1)

    def test_town_city_table_update(self):
        """Check buildings_reference.town_city table updates correctly."""
        self.reference_frame.chbx_town.setChecked(True)

        btn_ok = self.reference_frame.msgbox.button(QMessageBox.Ok)
        QTimer.singleShot(500, btn_ok.click)

        self.reference_frame.update_clicked(commit_status=False)

        # deleted town city
        sql_removed = "SELECT count(*)::integer FROM buildings_reference.town_city WHERE external_city_id = 1002;"
        result = db._execute(sql_removed)
        count_removed = result.fetchone()[0]
        self.assertEqual(count_removed, 0)
        # new town city
        sql_added = "SELECT count(*)::integer FROM buildings_reference.town_city WHERE external_city_id = 1003;"
        result = db._execute(sql_added)
        count_added = result.fetchone()[0]
        self.assertEqual(count_added, 1)
        # updated town city
        sql_upated = "SELECT name FROM buildings_reference.town_city WHERE external_city_id = 1001;"
        result = db._execute(sql_upated)
        name_updated = result.fetchone()[0]
        self.assertEqual(name_updated, "Wellington City")
        # check bulk_load_outlines
        sql_blo = "SELECT count(DISTINCT town_city_id)::integer FROM buildings_bulk_load.bulk_load_outlines;"
        result = db._execute(sql_blo)
        blo_town_update = result.fetchone()[0]
        self.assertEqual(blo_town_update, 2)
        # check building_outlines
        sql_bo = "SELECT count(DISTINCT town_city_id)::integer FROM buildings.building_outlines;"
        result = db._execute(sql_bo)
        bo_town_update = result.fetchone()[0]
        self.assertEqual(bo_town_update, 2)

    def test_territorial_authority_table_update(self):
        """Check buildings_reference.territorial_authority table updates correctly"""
        self.reference_frame.chbx_ta.setChecked(True)

        btn_ok = self.reference_frame.msgbox.button(QMessageBox.Ok)
        QTimer.singleShot(500, btn_ok.click)

        self.reference_frame.update_clicked(commit_status=False)

        # deleted TA
        sql_removed = "SELECT count(*)::integer FROM buildings_reference.territorial_authority WHERE external_territorial_authority_id = 10002;"
        result = db._execute(sql_removed)
        count_removed = result.fetchone()[0]
        self.assertEqual(count_removed, 0)
        # added TA
        sql_added = "SELECT count(*)::integer FROM buildings_reference.territorial_authority WHERE external_territorial_authority_id = 10003;"
        result = db._execute(sql_added)
        count_added = result.fetchone()[0]
        self.assertEqual(count_added, 1)
        # Check TA Grid view has been refreshed
        sql_removed_grid = """
        SELECT count(*)::integer
        FROM buildings_reference.territorial_authority_grid
        WHERE external_territorial_authority_id = 10002;
        """
        result = db._execute(sql_removed_grid)
        count_removed_grid = result.fetchone()[0]
        self.assertEqual(count_removed_grid, 0)
        sql_added_grid = """
        SELECT count(*)::integer
        FROM buildings_reference.territorial_authority_grid
        WHERE external_territorial_authority_id = 10003;"""
        result = db._execute(sql_added_grid)
        count_added_grid = result.fetchone()[0]
        self.assertTrue(count_added_grid > 0)
        # check bulk_load_outlines
        sql_blo = "SELECT count(DISTINCT territorial_authority_id)::integer FROM buildings_bulk_load.bulk_load_outlines;"
        result = db._execute(sql_blo)
        blo_ta_update = result.fetchone()[0]
        self.assertEqual(blo_ta_update, 2)
        # check building_outlines
        sql_bo = "SELECT count(DISTINCT territorial_authority_id)::integer FROM buildings.building_outlines;"
        result = db._execute(sql_bo)
        bo_ta_update = result.fetchone()[0]
        self.assertEqual(bo_ta_update, 2)
