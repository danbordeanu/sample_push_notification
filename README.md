# PUSH NOTIFICATION INFRA

A python-based application capable of sending notification using websockets and REST/API calls

## Introduction

This is a very complex application capable of making job status queries by calling the HPC-API and writing the job status 
to a websocket.

## Instalation

#### Prerequisites

Project requires 3 services in order to run and a few python libs

- rabbitmq-server
- memcached
- nginx (optional, but recommended). Nginx.conf is provided in git(EXTERNAL_CONFIGS/nginx)

Installing pip packages

```bash
pip install -r NOTIFICATIOS_QUEUE/requirements.txt 
```


Starting the PUSHNOTIFICATION

!!!NB!!! Change the config.ini settings in order to connect to a different host running rabbitmq/memcached. 
By default PUSHNOTIFICATION is connecting to localhost.

### OPTION B: Installing using the TEST/push_testing_menu.sh 

This method is used _only for local developement/testing. It's using a mocked HPC-API endpoint that will return DONE for any job status.


- STARTALL this will start all services, push notification and the hpc-api mock endpoint
- SOCKET-A create a web socket for user dan (for testing we used two users: dan/alex)
- GETSTATUS-A this will make rest/api call to get job status
- LOGS show logs
- KILLALL kill everything (push, socket, mock)
- DOCKER-START this will create all docker instances: mock, rabbit, memcached, ngnix and push notification
- DOCKER-STOP kill all containers

### OPTION C: Installing using docker-compose

This is the recommended way to deploy the service. It requires running docker service


```bash
cd DOCKER/x64
docker-compose up -d
```

Compose will deploy all services: memcached, ngninx, rabbitmq and pushnotification

Service is accesible calling the nginx port:8887, all request are redirected to pushnotification:8889

!!!NB!!! This is using the real HPC-API endpoint, so real ticket and jobs must be provided.

For a **local test env** where the real HPCAPI is not required, please use the docker-compose-mock.ym file.
It will create also the http_mock server
 
 ```bash
cd DOCKER/X64
docker-compose -f docker-compose-mock.ymm up -d

```
 ## Testing
 

### Creating a websocket

```bash
 wscat -c ws://localhost:8887/register?userid=bordeanu
```

### Seding a get request

```bash
curl http://localhost:8887/push?userid=bordeanu&ticket=bla.host.com&jobid=3781
```

**!!!NB!!!** Please do keep in mind this require a real ticket/userid and a real jobid

If the jobe has status DONE, the response is written on the websocket

```bash
"[{"REST_tornado - jobstatus: ": {"STATUS": "DONE", "JOB_NUMBER": "3781"}}, {" Iteration ": 2}"
```

When testing in combination with the mock, any username/ticket/job id can be used. The mock will **always** return DONE for any job.

```bash
curl http://localhost:8887/push?userid=dan&ticket=bla.host.com&jobid=123

```


### LOGS

docker-compose is using the default docker logs. There are no options configured for logger service.

```bash
docker logs x64_push_1
```
