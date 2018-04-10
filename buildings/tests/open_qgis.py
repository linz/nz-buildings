import os
import re
import sys
from pexpect import run
from pipes import quote


"""
This is a python script called by the makefile to run the tests on
the buildings_plugin.
based on boundlessgeo  testrunner.py

"""


def open_qgis():

    print "---------------------------------------"
    print "             Opening QGIS   "
    print "---------------------------------------"

    os.environ['QGIS_DEBUG'] = '1'
    args = [
        'qgis',
        os.environ.get('QGIS_EXTRA_OPTIONS', ''),
        '--nologo',
        '--noversioncheck',
        '--code',
        '~/.qgis2/python/plugins/local_buildings/tests/test_runner.py',
    ]

    command_line = ' '.join(args)
    print("QGIS Test Runner - launching QGIS as %s ..." % command_line)
    out, returncode = run("sh -c " + quote(command_line), withexitstatus=1)

    ok = out.find('(failures=') < 0 and \
        len(re.findall(r'Ran \d+ tests in\s',
                       out, re.MULTILINE)) > 0
    print('='*60)
    values = out.split(" ")

    final = []
    for index, val in enumerate(values):
        if "test_" in val:
            final.append(val)
            final.append('...')
            if 'roads' in values[index + 2]:
                final.append(values[index + 2])
        if "setup_main_toolbar\r\n\r\n----------------------------------------------------------------------\r\nRan" in val:
            final.append('\n')
            final.append(val)
            final.append(' ' + values[index + 1] + ' ' + values[index + 2] + ' ' + values[index + 3] + ' ' + values[index + 4])
    str2 = ''.join(final)
    print str2

    if len(out) == 0:
        print("QGIS Test Runner - [WARNING] subprocess returned no output")
    print('='*60)
    print("QGIS Test Runner - %s bytes returned and finished with exit code: %s" % (len(out), 0 if ok else 1))
    sys.exit(0)
