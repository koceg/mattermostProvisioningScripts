#!/bin/bash

cat<<EOF
Configuring Mattermost
----------------------

Creating Teams and Channels
---------------------------
EOF
MMPORT=8085
CHANNELS="update channels set createat=0,updateat=0,deleteat=0,creatorid=0;"
TEAMS="update teams set createat=0,updateat=0,deleteat=0,email='';"
CHANNELMEMBERS="update channelmembers set lastviewedat=0,lastupdateat=0;"
MMTOKEN=$(docker exec postgresql \
  psql -U mattermost -t -c "select token from useraccesstokens;")
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
