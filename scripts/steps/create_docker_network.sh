#!/bin/sh

echo >&2 ""
echo >&2 "###########################"
echo >&2 "# Creating Docker network #"
echo >&2 "###########################"
echo >&2 ""

docker network create $DOCKER_NETWORK