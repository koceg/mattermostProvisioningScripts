from minio import Minio
from minio.error import ResponseError
import time
import psycopg2

def minioLogin(minioUrl,accessKey,secretKey,port=9000,tls=False):
    return Minio('{}:{}'.format(minioUrl,port),
                access_key=accessKey,
                secret_key=secretKey,
                secure=tls)

def pgLogin(pgUsername,pgPassword,pgHostname,pgDatabase='mattermost',pgPort=5432):
    dsn = 'postgres://{}:{}@{}:{}/{}?sslmode=disable\u0026connect_timeout=10'\
            .format(pgUsername,pgPassword,pgHostname,pgPort,pgDatabase)
    return psycopg2.connect(dsn)


class MinioClient():
    """MinioClient is a wrapper to 'MOVE' files from one path to another"""

    destination = None
    source = None

    def __init__(self,minioConnect,pgConnect,bucketName='mattermost'):
        self.bucket = bucketName
        self.pg = pgConnect
        self.cur = self.pg.cursor()
        self.client = minioConnect

    def filePath(self,channelId,userId,fileId,fileName):
        """Return path to bucket object speciffic to mattermost"""
        return "{}/teams/noteam/channels/{}/users/{}/{}/{}".format(
                time.strftime('%Y%m%d'),
                channelId,
                userId,
                fileId,
                fileName)

    def fileMove(self,destinationPath,sourcePath,sourceBucket='mattermost'):
        """Move file from source to destination path"""
        self.destination = destinationPath
        self.source = "/{}/{}".format(sourceBucket,sourcePath)
        try:
            self.client.copy_object(self.bucket,self.destination,self.source)
            self.client.remove_object(sourceBucket,sourcePath)
        except ResponseError as err:
            print(err)

    def pgPostUpdate(self,fileId,postId):
        """Append new file to existing mattermost post"""
        postAppendFile="update posts \
                set fileids='[\"{}\"]' \
                where id='{}';".format(fileId,postId)
        self.cur.execute(postAppendFile)
    
    def pgFilePathUpdate(self,creatorId,postId,path,fileId):
        """Update path and author for mattermost file"""
        filePathAndAuthorUpdate="update fileinfo \
                set creatorid='{}',postid='{}',path='{}' \
                where id='{}';".format(creatorId,postId,path,fileId)
        self.cur.execute(filePathAndAuthorUpdate)
        self.pg.commit()
