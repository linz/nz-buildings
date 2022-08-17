#!/bin/sh

echo >&2 ""
echo >&2 "#######################"
echo >&2 "# Running pgTAP tests #"
echo >&2 "#######################"
echo >&2 ""

docker exec db pg_prove -v /nz-buildings/db/tests
