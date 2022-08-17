#!/bin/sh

echo >&2 ""
echo >&2 "#################"
echo >&2 "# Sqitch revert #"
echo >&2 "#################"
echo >&2 ""

docker exec --workdir /nz-buildings/db/sql db sqitch revert -y
