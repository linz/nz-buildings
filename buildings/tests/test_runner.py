
import unittest
import os
import getpass


test_cases = []
test_modules = []


def update_unique_test_modules(test_folder):
    """
    Loops through all TestCase instances in a test folder to find
    unique test modules
    """
    unittest.TestLoader().discover(test_folder, pattern="test_*.py")

login = getpass.getuser()
path = os.path.join('/home', login, '.qgis2/python/plugins/local_buildings/tests')

update_unique_test_modules(path)
