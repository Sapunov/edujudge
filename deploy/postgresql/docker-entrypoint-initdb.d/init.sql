CREATE USER dba WITH PASSWORD 'somestrongpassword';

CREATE DATABASE db;

GRANT ALL PRIVILEGES ON DATABASE db to dba;
ALTER USER dba CREATEDB;