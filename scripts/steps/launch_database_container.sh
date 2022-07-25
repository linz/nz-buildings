#!/bin/sh

docker run \
--name db \
-p $PGPORT:$PGPORT \
--volume $BASE_DIR:/nz-buildings \
--net $DOCKER_NETWORK \
-e "PGHOST=$PGHOST" \
-e "PGPORT=$PGPORT" \
-e "PGUSER=$PGUSER" \
-e "PGPASSWORD=$PGPASSWORD" \
-e "POSTGRES_USER=$PGUSER" \
-e "POSTGRES_PASSWORD=$PGPASSWORD" \
-d \
$DB_DOCKER_IMAGE

RETRIES=3
until docker exec -u postgres db pg_isready || [ $RETRIES -eq 0 ]; do
RETRIES=$((RETRIES-=1))
echo "Waiting for postgres, $RETRIES attempts remaining..."
sleep 10;
done
