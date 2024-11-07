# -*- coding: utf-8 -*-

"""This module converts .ini files to Python objects."""

import os
from configparser import ConfigParser
from typing import Dict, List, Optional

from qgis.core import QgsApplication

CONFIG_FILE_PATH = os.path.join(QgsApplication.qgisSettingsDirPath(), "buildings", "config.ini")
CONFIG_SCHEMA = {
    "database": ["host", "port", "dbname", "user", "password"],
    "api": ["linz", "statsnz"],
    "logging": ["logfile"]
}


def validate_config(config: Dict[str, List[str]]) -> Optional[List[str]]:
    """
    Checks that the supplied config has the same sections and keys as CONFIG_SCHEMA.
    Values are not validated. If there are any errors, we return a list of strings
    describing each error.
    """
    errors = []
    for schema_section, schema_keys in CONFIG_SCHEMA.items():
        config_section = config.get(schema_section, None)
        if config_section is None:
            errors.append(f"- Section [{schema_section}] missing")
        else:
            for schema_key in schema_keys:
                if schema_key not in config_section:
                    errors.append(f'- Key "{schema_key}" missing from section [{schema_section}]')
    if errors:
        return errors


def read_config_file(file_path: os.PathLike = CONFIG_FILE_PATH) -> Dict[str, Dict[str, str]]:
    """
    Parses the config file from disk, and returns its contents as a dictionary with keys of each
    ini section, and and values of a dictionary of key value pairs of items inside that section.

    # Example ini file
    [section]
    key_1 = value_1
    key_2 = value_2

    # Parsed dictionary
    {"section": {"key_1": "value_1", "key_2": "value_2"}}

    A RuntimeError exception will be raised if the config file (defined in CONFIG_FILE_PATH) either
    does not exist, is unable to be parsed, or does not contain the required sections and keys
    (defined in CONFIG_SCHEMA).
    """
    if not os.path.isfile(file_path):
        raise RuntimeError(f'Config file "{CONFIG_FILE_PATH}" not found.')
    try:
        parser = ConfigParser()
        parser.read(file_path)
        config = {section: dict(parser.items(section)) for section in parser.sections()}
    except Exception as err:
        raise RuntimeError(f'Unable to parse config file "{CONFIG_FILE_PATH}"') from err
    validation_errors = validate_config(config)
    if validation_errors is not None:
        raise RuntimeError(f'Config file "{CONFIG_FILE_PATH}" has errors:\n' + "\n".join(validation_errors))
    return config
