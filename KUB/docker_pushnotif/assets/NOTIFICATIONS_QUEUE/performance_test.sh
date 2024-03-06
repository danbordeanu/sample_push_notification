#!/usr/bin/env bash

COUNT=0

while true; do
sleep 2
COUNT=$((COUNT+1))
echo $COUNT
curl 'http://localhost:8889/push?userid=mimi&ticket=23456789&jobid=199'
done