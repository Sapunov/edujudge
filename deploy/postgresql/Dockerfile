FROM onjin/alpine-postgres:9.6

RUN mkdir -p /docker-entrypoint-initdb.d

COPY docker-entrypoint-initdb.d/* /docker-entrypoint-initdb.d/
