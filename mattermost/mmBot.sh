#!/bin/bash

MMPORT=$2
MMUSER=$1
MMUSERID=$(docker exec postgresql \
  psql -U mattermost -t -c "select id from users where username='$MMUSER'" | \
  tr -d [:blank:] )
MMTOKEN=$(docker exec postgresql \
  psql -U mattermost -t -c "select token from useraccesstokens \
  where userid='$MMUSERID'")
MMADDRESS=$(docker inspect \
  --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mattermost)
MINIOADDRESS=$(docker inspect \
  --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' minio)
MINIOACCESSKEY=$(docker inspect \
  --format '{{ index (index .Config.Env) 0 }}' minio | cut -d\= -f2 )
MINIOSECRETKEY=$(docker inspect \
  --format '{{ index (index .Config.Env) 1 }}' minio | cut -d\= -f2 )
PGUSERNAME=$(docker inspect \
  --format '{{ index (index .Config.Env) 0 }}' postgresql | cut -d\= -f2 )
PGPASSWORD=$(docker inspect \
  --format '{{ index (index .Config.Env) 1 }}' postgresql | cut -d\= -f2 )
PGHOSTNAME=$(docker inspect \
  --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' postgresql)

python3 mmBot.py $MMTOKEN $MMADDRESS $MMPORT \
  $MINIOADDRESS $MINIOACCESSKEY $MINIOSECRETKEY \
  $PGUSERNAME $PGPASSWORD $PGHOSTNAME
