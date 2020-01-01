#!/bin/bash

cat<<EOF
Configuring Mattermost
----------------------

Creating Teams and Channels
---------------------------
EOF
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
if [[ ! -z $TOKEN ]]
then
./mmCreateTeams.py $MMTOKEN $MMADDRESS $MMPORT
else
  echo "mattermost token not configured"
  exit 1
fi
echo "Done!"
