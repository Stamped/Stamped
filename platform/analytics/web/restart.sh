#!/usr/bin/env bash
# utility script to quickly / cleanly update and restart the dev web server on ec2

git pull

stop analytics
stop nginx_analytics

rm -rf /stamped/www/cache

start analytics
start nginx_analytics

