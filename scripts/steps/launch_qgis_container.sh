#!/bin/sh

echo >&2 ""
echo >&2 "############################"
echo >&2 "# Launching QGIS container #"
echo >&2 "############################"
echo >&2 ""

docker run \
--name qgis \
--volume $BASE_DIR:/tests_directory \
--volume /tmp/.X11-unix:/tmp/.X11-unix \
--net $DOCKER_NETWORK \
-e DISPLAY=$QGIS_DISPLAY \
-e QT_LOGGING_RULES='*.debug=false;qt.qpa.*=false' \
-d \
$QGIS_DOCKER_IMAGE

sleep 5
