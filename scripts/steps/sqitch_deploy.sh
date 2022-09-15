#!/bin/sh

echo >&2 ""
echo >&2 "#################"
echo >&2 "# Sqitch deploy #"
echo >&2 "#################"
echo >&2 ""

docker exec --workdir /nz-buildings/db/sql db sqitch deploy
