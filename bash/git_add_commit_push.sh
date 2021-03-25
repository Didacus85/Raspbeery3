#!/bin/bash

TIMESTAMP=$(date +%Y-%m-%d_%T)

cd /home/pi/env/Raspbeery3

git add .
#git add raspbeery.py

git commit -m "Commit $TIMESTAMP"
#git commit raspbeery.py -m "Commit $TIMESTAMP"

#git push origin master

git push https://Nomeutente:Password@github.com/Didacus85/Raspbeery3.git master
