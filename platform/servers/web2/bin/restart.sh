#!/usr/bin/env bash
# utility script to quickly / cleanly update and restart the dev web server on ec2

git pull

stop web
stop nginx_web

rm -rf /stamped/www/cache

cd /stamped/stamped/platform/servers/web2 && make

start web
start nginx_web

