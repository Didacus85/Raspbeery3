#!/bin/bash

cd /home/pi/env/Raspbeery3

git fetch origin master
git reset --hard origin/master
git pull origin master

