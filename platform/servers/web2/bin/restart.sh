#!/usr/bin/env bash
# utility script to quickly / cleanly update and restart the dev web server on ec2

git pull

stop nginx_web
stop gunicorn_web

rm -rf /stamped/www/cache

cd /stamped/stamped/platform/servers/web2 && make clean all

start gunicorn_web
start nginx_web

