
import unittest
import os
import getpass


def run_test_modules(test_folder):
    """
    Loops through all TestCase instances in a test folder to find
    unique test modules
    """
    # unittest.TestLoader().discover(test_folder, pattern="test_setup*.py")
    # unittest.TestLoader().discover(test_folder, pattern="test_processes*.py")
    unittest.TestLoader().discover(test_folder, pattern="test_setup_a*.py")
    unittest.TestLoader().discover(test_folder, pattern="test_processes_a*.py")


login = getpass.getuser()
path = os.path.join('/home', login, '.qgis2/python/plugins/buildings/tests')

run_test_modules(path)
