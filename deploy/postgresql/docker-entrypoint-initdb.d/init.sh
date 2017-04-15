#!/bin/bash

echo "host  all     all     0.0.0.0/0       md5"    >> /var/lib/postgresql/data/pg_hba.conf && \
echo "listen_addresses = '*'"                       >> /var/lib/postgresql/data/postgresql.conf && \
echo "max_connections = 100"                        >> /var/lib/postgresql/data/postgresql.conf && \
echo "shared_buffers = 131070"                      >> /var/lib/postgresql/data/postgresql.conf && \
echo "log_statement = none"                         >> /var/lib/postgresql/data/postgresql.conf
