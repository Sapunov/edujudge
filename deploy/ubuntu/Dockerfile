FROM ubuntu:16.04

MAINTAINER Sapunov Nikita

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN apt-get update \
	&& apt-get install -y apt-utils \
	&& apt-get upgrade -y \
	&& apt-get purge locales \
	&& apt-get install -y locales

RUN locale-gen en_US.UTF-8

RUN apt-get install -y python python3 \
		python3-pip python3-dev nginx supervisor uwsgi-plugin-python3 vim \
	&& pip3 install -U pip uwsgi
