FROM ubuntu:16.04
MAINTAINER Sapunov Nikita

RUN apt-get update \
	&& apt-get -y upgrade \
	&& apt-get install -y python python3 \
		python3-pip python3-dev nginx supervisor uwsgi-plugin-python3 \
	&& pip3 install -U pip
