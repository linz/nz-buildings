#!/bin/sh

docker exec --workdir /nz-buildings/db/sql db sqitch deploy
