# Pull base image.
FROM base-image.dock.com/ubuntu/18.04/rel-2018w43

# let's have a nice motd message
COPY DOCKER/X64/docker_pushnotif/assets/motd /etc/motd

# let's have wait for it

ADD DOCKER/X64/docker_pushnotif/assets/wait_for_it.sh /usr/local/bin/

# let's make the opt dir

RUN mkdir -p /opt/pushnotification/
RUN mkdir -p /opt/pushnotification/COMMONS
RUN mkdir -p /opt/pushnotification/NOTIFICATIONS_QUEUE

# let's add the code of the push

COPY COMMONS/ /opt/pushnotification/COMMONS
COPY NOTIFICATIONS_QUEUE/ /opt/pushnotification/NOTIFICATIONS_QUEUE

# let's set the local proxy
RUN echo 'Acquire::http::Proxy "http://webproxy.host.com:8080";' >> /etc/apt/apt.conf
RUN echo 'Acquire::https::Proxy "https://webproxy.host.com:8080";' >> /etc/apt/apt.conf

#let's update
RUN apt-get update

#let's install the internet
RUN apt-get install -y --force-yes \
		apt-utils \ 
		supervisor \
		wget \
		htop \
		nginx\
		telnet \
		python \
		python-pip \
	&& rm -rf /var/lib/apt/lists/*


#let's have the localproxy

RUN export http_proxy=webproxy.host.com:8080
RUN export http_proxy=webproxy.host.com:8080


# let's install python dependencies list
RUN pip install requests requests-oauthlib requests-toolbelt futures tornado pika python-memcached-stats pymemcache singledispatch backports_abc six websocket-client multi-mechanize matplotlib --proxy=webproxy.host.com:8080 

WORKDIR /opt/pushnotification/NOTIFICATIONS_QUEUE
EXPOSE 8889

# Define default command.
#CMD ["python","NotificationServer_QUEUE.py"]

# Define default command.
CMD /usr/local/bin/wait_for_it.sh -h $RABBITMQ_HOST -p $RABBITMQ_PORT --timeout=50 --strict -- \
    "python NotificationServer_QUEUE.py"


