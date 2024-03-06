# Graylog permanent log storage

## Dependencies

Docker must be installed on the machine also docker-compose must be accessible.
If docker is in internal MERCK network proxy must be configured

````bash
mkdir /etc/systemd/system/docker.service.d
touch http-proxy.conf
touch https-proxy.conf

````

**!!!NB!!! since graylog containers are self signed the MERCK proxy might stop/deny the download of the images.**

## How to start

```bash
docker-compose up -d
```

##  Container started by graylog

```bash
graylog/graylog:2.4.0-1                               
mongo:3                                               
docker.elastic.co/elasticsearch/elasticsearch:5.6.3
```

## How to configure the pushnotification services to use the graylog infra

Add this for every service that will use the graylog

```bash
logging:
      driver: "gelf"
      options:
        gelf-address: "udp://localhost:12201"
        tag: "first-logs"
```

**!!!!!NB!!!! By enabling a different logger driver the docker logs * will stop working**

There is also a docker-compose-mock-logs.yml recipe for docker-compose that will start the pushnotification containers with logs support

```bash
docker-compose -f docker-compose-mock-logs.yml up -d

```

## GRAYLOG docs

http://docs.graylog.org/en/2.4/pages/dashboards.html#widget-types

http://docs.graylog.org/en/2.4/pages/dashboards.html

http://docs.graylog.org/en/2.4/pages/queries.html