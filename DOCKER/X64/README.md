# Docker compose file

## Dependencies

Docker must be installed on the machine also docker-compose must be accessible.
If docker is in internal bla network proxy must be configure
````bash
mkdir /etc/systemd/system/docker.service.d
touch http-proxy.conf
touch https-proxy.conf

````

Add in conf files 

```bash
[Service]
Environment="HTTPS_PROXY=http://webproxy,bla.com:8080"

```

!!!!NB!!!!
Please set the bind dir according to your disk location(change device param value with Notification code location) where code is running.

```bash
volumes:
  app_sourcecode:
    driver_opts:
      type: none
      device: /home/dan/Work/pushnotif_deploy/
      o: bind
```

## How to run

```bash
docker-compose up -d
```
This will build/build all the docker images:
 - docker_nginx 
 - docker_memcache
 - docker_rabbit
 - docker_push

In order to run the http_mock, run 

!!!NB!!!! Use this only for internal testing (it's not using a real HPC_API)
```bash
docker-compose -f docker-compose-mock.yml up -d
```
## Images

### docker_nginx

Docker file is located in docker_nginx directory.
Image is binding on port 8887 and is redirecting to upsteam app(push) port 8889. Please refer to
nginx.conf file

```bash
 # Enumerate all the Tornado servers here
    upstream frontends {
        server push:8889;
    }
```

### docker_memcache

Docker file is located in docker_memcached directory.
Image is binding on port 11211. 

### docker_pushnotif

Docker file is located in docker_pushnotif and it's containing the NotificationServer code.
Image is binding on port 8889. It's possible to connect directly to 8889, but we do recommend to use the nginx frontend:8887

### docker_rabbitmq

ATM we pool the official rabbitmq image from docker official registry. 


### docker_mock

This container will be running the hpcapi_mock. When started the push notification will use env HPCAPI_URL=http://mock:8081/api/v2 instead of using the real HPC API

Please do read the docker-compose.mock.yml file

To start run 

````bash
docker-compose -f docker-compose.mock.yml up -d
````


## Testing

### Creating a websocket

```bash
 wscat -c ws://localhost:8887/register?userid=bordeanu
```

### Seding a get request

```bash
"curl http://localhost:8887/push?userid=bordeanu&ticket=ST-67-UNewNC1n2EgfgcNjHNys-bla-dev.bla.com&jobid=3781"
```

If the jobe has status DONE, the response is written on the websocket

```bash
"< [{"REST_tornado - jobstatus: ": {"STATUS": "DONE", "JOB_NUMBER": "3781"}}, {" Iteration ": 2}]"

```