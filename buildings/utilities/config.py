# -*- coding: utf-8 -*-

"""This module converts .ini files to Python objects."""

import configparser
import os


def _parse_config_to_dict(config_parser):
    """Returns a dictionary containing config section names as the key and
    a dictionary of config item names and config item values as the value.
    e.g. config['section_name']['item_name'] provides the item_value.
    """
    config = {}
    for section in config_parser.sections():
        config[section] = dict(config_parser.items(section))
    return config


def read_config_file(file_path):
    """Check that the provided config file name exists and if so, read it into a
    ConfigParser() object"""
    config_parser = None
    if os.path.isfile(file_path):
        config_parser = configparser.configparser()
        config_parser.read(file_path)
    else:
        raise IOError("Config file not found.")
    config = _parse_config_to_dict(config_parser)
    return config
