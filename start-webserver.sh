#!/bin/sh


ps aux | grep webserver | awk '{if ($14 == 9091)print $2}'  | xargs kill > /dev/null 2>&1

python webserver.py  app:application 9091  > ./mpd_server.log  &
