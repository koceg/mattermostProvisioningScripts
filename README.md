### Mattermost
Goal of this repo is to automate deployment and some initialization work that is mandatory when setting up new mattermost instance in a programmatic way.

### Prerequisite

-	docker version 19.03.4 or later
-	docker-compose version 1.24.1 or later
-	python3 on the host where docker and the scripts are going to run
	-	NOTE: scripts can run on any host if configured properly (mmBot.sh,mmConfig.sh)
-	[python mattermost driver](https://github.com/Vaelor/python-mattermost-driver)

`docker-compose.yml` required images that should be available(accessible by default unless firewall rules or other settings prevent that):   

-	postgres:alpine
-	minio:latest
-	docker.elastic.co/elasticsearch/elasticsearch:6.8.0
-	mattermost:5.17.0 (or later)
	- Disclaimer: I'm using custom dockerfile based on the official mattermost dockerfile but should work with slight modification if errors occur
-	mountpoints **mattermost,elasticsearch,mattermost** should exist somewhere on the system where docker is running   
and `mattermost/config.json` needs to be present   

To have a successful demonstration of the scrips we'll do the following step:
```
mkdir -p /tmp/{minio/mattermost,elasticsearch,mattermost}
cp mattermost/config.json /tmp/mattermost
```

### Installation

First we need to create a docker network so the containers be able to resolve their container names
```
docker network create --driver=bridge --subnet=10.0.0.0/24 mattermost
```

inside `docker-compose.yml` the following parameters need to be set up

-	POSTGRES_USER
-	POSTGRES_PASSWORD
-	MINIO_ACCESS_KEY
-	MINIO_SECRET_KEY
-	volume mountpoints SHOULD be changed for the mentioned `mkdir` cmd above
-	Optional ports can be changed inside this file as well   

Once all of the above is completed we start our mattermost setup by calling from inside `docker-compose.yml` directory
```
docker-compose up # Create and start containers
```

on our terminal we'll see the output of our newly created containers and the errors that we might encounter during start

Once we are done we can stop them by pressing `CTRL+C` and for every other consecutive run we execute
```
docker-compose start
docker-compose stop
```

### **NOTE: before trying to start the following scrips we need to do initial login to mattermost to create system admin and to generate access token**

```
(Account Settings)->(Security)->(Personal Access Tokens)->(edit)->(Create New Token)
```
after this the shell scripts do all the work

#### mmConfig.sh
is our script that calls `mmCreateTeams.py` with the required parameters and creates our teams and channels under teams respectively

#### mmBot.sh

Starts our `mmBot.py` script which monitors on all of the channels where our bot (script) is a member and prevents (deletes) every attempt of users trying to post direct messages or uploads to that channel.
Can be useful if we want all files to originate from one user and that is what our script does here. 

If a user wants to upload something it sends the files as a direct post to our bots username and adds a text message in the format `team:channel` where should the files be uploaded.Our bot then moves the newly uploaded files in the correct path and creates new post with the content of a single file with text message  `fileName:(actual name of the file)` can be easily changed for other scripting logic inside `mmBot.py`

#### mmMinioClass.py

Contains connectors to minio, postgresql and implements `MinioClient class`. Reason for this is to provide a way to MOVE files inside s3 buckets because there is currently no direct way to do this with the s3 APIs, minio API or official aws s3 API. Logic here applies to mattermost s3 paths but is easily changeable for other applications