#!/bin/sh

LOGFILE="/tmp/qgis_testrunner_$$"
SCRIPT_FILE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/run.py"

unbuffer qgis --version-migration --nologo --code $SCRIPT_FILE 2>&1 | tee ${LOGFILE}

EXIT_CODE=$?
OUTPUT=$(cat $LOGFILE)

if [ -z "$OUTPUT" ]; then
    echo "ERROR: no output from the test runner! (exit code: ${EXIT_CODE})"
    exit 1
fi

echo "$OUTPUT" | grep -q "OK" && echo "$OUTPUT" | grep -q "Ran"
if [ "$?" -eq "0" ] ; then PASSED="True"; else PASSED="False"; fi

echo "$OUTPUT" | grep -q "FAILED"
if [ "$?" -eq "0" ] ; then FAILED="True"; else FAILED="False"; fi

echo "$OUTPUT" | grep "QGIS died on signal"
if [ "$?" -eq "0" ] ; then DIED="True"; else DIED="False"; fi

echo "Test results: PASSED=$PASSED FAILED=$FAILED DIED=$DIED"

if [ "$PASSED" = "True" ] && [ "$FAILED" = "False" ] && [ "$DIED" = "False" ]; then exit 0; fi

exit 1
