sudo docker run -d \
	--name ejudge \
	--link redisserver:redisserver \
	--link postgres:postgres \
	-p 8080:80 \
	-v ejudgedata:/var/lib/judge/data \
	edujudge:devel
