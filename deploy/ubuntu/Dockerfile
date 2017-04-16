FROM ubuntu:16.04

MAINTAINER Sapunov Nikita

# Set the locale
RUN locale-gen en_US.UTF-8

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN apt-get update \
	&& apt-get install -y --no-install-recommends apt-utils \
	&& apt-get upgrade -y

RUN apt-get install -y python python3 \
		python3-pip python3-dev nginx supervisor uwsgi-plugin-python3 \
	&& pip3 install -U pip uwsgi
