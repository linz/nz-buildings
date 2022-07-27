#!/bin/sh

echo >&2 ""
echo >&2 "###############"
echo >&2 "# Cleaning up #"
echo >&2 "###############"
echo >&2 ""

docker container stop db && docker container rm db
docker container stop qgis && docker container rm qgis
docker network rm buildings
