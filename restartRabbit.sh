#!/bin/bash

sudo rabbitmqctl  stop_app
sudo rabbitmqctl  reset
sudo rabbitmqctl  start_app
sudo rabbitmqctl  status
sudo rabbitmqctl  list_queues

sudo /etc/init.d/memcached restart
