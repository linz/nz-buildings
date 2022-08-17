#!/bin/sh

echo >&2 ""
echo >&2 "##############################"
echo >&2 "# Running QGIS interactively #"
echo >&2 "##############################"
echo >&2 ""

xhost +
docker exec qgis qgis
