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

# These functions are the logic behind displaying warnings to the iface and thus user,
# and catch raised errors
"""

from qgis.gui import QgsMessageBar
from qgis.utils import iface


def buildings_warning(warn_text, warn_message, warn_level_text):
    """
    push message to messageBar

    @param warn_text:           warning type
    @type warn_text:            string
    @param warn_message         message to display to user
    @type warn_message          string
    @param warn_level_text      level of warning
    @type warn_level_text       string
    """
    if warn_level_text == "info":
        warn_level = QgsMessageBar.INFO
        warn_duration = 5
    elif warn_level_text == "warning":
        warn_level = QgsMessageBar.WARNING
        warn_duration = 5
    elif warn_level_text == "critical":
        warn_level = QgsMessageBar.CRITICAL
        warn_duration = 0

    iface.messageBar().pushMessage(
        warn_text,
        warn_message,
        level=warn_level, duration=warn_duration
    )
