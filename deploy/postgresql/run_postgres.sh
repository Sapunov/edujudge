#!/bin/bash

sudo docker run --name postgres \
	-e POSTGRES_PASSWORD=somestrongpassword \
	-v pgdata:/var/lib/postgresql/data \
	-d judge-postgres:latest
