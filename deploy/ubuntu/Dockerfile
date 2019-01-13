FROM python:3.5-slim

RUN BUILD_DEPS='build-essential python3-dev' \
	&& apt-get update && apt-get install -y --no-install-recommends ${BUILD_DEPS} \
	&& apt-get install -y --no-install-recommends nginx supervisor uwsgi-plugin-python3 vim \
	&& pip3 install -U pip uwsgi
