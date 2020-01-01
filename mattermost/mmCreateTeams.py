#!/usr/bin/python3
import sys
from mattermostdriver import Driver

teams=["team1","team2","team3","etc."]
channels={
         "team1":["channel1","channel2","channel3","etc."],
         "team2":["channel1","channel2","channel3","etc."],
         "team3":["channel1","channel2","channel3","etc."],
         "etc.":["channel1","channel2","channel3","etc."],
         }

if __name__== "__main__":

    options={
            'verify': False,
            'url': '{}'.format(sys.argv[2]),
            'port': int(sys.argv[3]),
            'scheme': 'http',
            'token': '{}'.format(sys.argv[1])
            }
    try:

        mmClient=Driver(options)
        bot=mmClient.login()

        for team in teams:

            payload={
                    "display_name":team.lower(),
                    "name":team.lower(),
                    "type":'O'
                    }

            teamId=mmClient.teams.create_team(options=payload)['id']

            mmClient.teams.patch_team(
                   team_id=teamId,
                   options={
                           'allow_open_invite':True
                           })

            mmClient.teams.add_user_to_team(team_id=teamId,
                   options={
                            'team_id':teamId,
                            'user_id':bot['id']
                           })

            for channel in channels[team]:

                payload={
                        "team_id":teamId,
                        "name":channel.lower(),
                        "display_name":channel,
                        "type":'O'
                        }

                channelId=mmClient.channels.create_channel(options=payload)['id']

                mmClient.channels.patch_channel(
                        channel_id=channelId,
                        options={
                                'type':'O'
                                })

                mmClient.channels.add_user(
                        channel_id=channelId,
                        options={
                                'user_id':bot['id']
                                })

    except Exception as e:
        print("ERROR", e)
