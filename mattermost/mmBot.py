import asyncio
import sys
import json
import time
import mmMinioClass
from mattermostdriver import Driver

@asyncio.coroutine
def new_event(message):
   try:

        jsonMessage=json.loads(message)
        jsonPost=json.loads(jsonMessage['data']['post'])
        channeId=jsonMessage['broadcast']['channel_id']

        if jsonMessage['event'] == 'posted' and \
           jsonMessage['data']['channel_name'].find(bot['id']) != -1:

                    filePath=jsonPost['message'].split(':')
                    fileList=jsonPost['metadata']['files']

                    moveFiles(mmClient,minioClient,channeId,filePath,fileList)
                    mmClient.posts.delete_post(jsonPost['id'])

        elif jsonMessage['event'] != 'post_deleted' and \
                jsonPost['user_id'] != bot['id']:

                    # to monitor only selected channels make the bot part of
                    # them and no other or messages will star to dissapear
                    #if mmClient.channels.get_channel(channeId)['type'] != 'O':
                        mmClient.posts.delete_post(jsonPost['id'])

   except Exception as e:
       print(e)

def moveFiles(mattermost,minio,channelSource,filePath,fileList):

    team=mattermost.teams.get_team_by_name(filePath[0].strip())
    channel=mattermost.channels.get_channel_by_name(team['id'],filePath[1].strip())

    for newFile in fileList:

        sourcePath=minio.filePath(
                channelSource,
                newFile['user_id'],
                newFile['id'],
                newFile['name'])

        destinationPath=minio.filePath(
                channel['id'],
                bot['id'],
                newFile['id'],
                newFile['name'])

        minio.fileMove(destinationPath,sourcePath)
        
        # format the message that should be appended with the new file upload
        newPost={'channel_id': channel['id'],
                 'file_ids': [ newFile ],
                 'message': 'fileName:{}'.format(newFile['name'])
                }

        postId=mattermost.posts.create_post(options=newPost)['id']
        minio.pgPostUpdate(newFile['id'],postId)
        minio.pgFilePathUpdate(bot['id'],postId,destinationPath,newFile['id'])

options={
        'verify': False,
        'url': '{}'.format(sys.argv[2]),
        'port': int(sys.argv[3]),
        'scheme': 'http',
        'token': '{}'.format(sys.argv[1])
        }

minioLogin = mmMinioClass.minioLogin(sys.argv[4],sys.argv[5],sys.argv[6])
pgLogin = mmMinioClass.pgLogin(sys.argv[7],sys.argv[8],sys.argv[9])
minioClient = mmMinioClass.MinioClient(minioLogin,pgLogin)

mmClient=Driver(options)
bot=mmClient.login()
mmClient.init_websocket(new_event)
