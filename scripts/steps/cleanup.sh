#!/bin/sh

docker container stop db && docker container rm db
docker container stop qgis && docker container rm qgis
docker network rm buildings
