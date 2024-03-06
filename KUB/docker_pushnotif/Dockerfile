# Pull base image.
FROM debian:latest

# let's have a nice motd message
COPY assets/motd /etc/motd

# let's set the local proxy
RUN echo 'Acquire::http::Proxy "http://proxy.host.com:8080";' >> /etc/apt/apt.conf
RUN echo 'Acquire::https::Proxy "https://proxy.host.com:8080";' >> /etc/apt/apt.conf



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

RUN export http_proxy=proxy.host.com:8080
RUN export http_proxy=proxy.host.com:8080


# let's have the wait_for_it_script.sh
ADD assets/wait_for_it.sh /usr/local/bin/


# let's make the opt dir

RUN mkdir -p /opt/pushnotification/


# let's copy push notif

COPY assets/COMMONS /opt/pushnotification/COMMONS
COPY assets/NOTIFICATIONS_QUEUE /opt/pushnotification/NOTIFICATIONS_QUEUE

# let's install python dependencies list
RUN pip install requests requests-oauthlib requests-toolbelt futures tornado pika python-memcached-stats pymemcache singledispatch backports_abc six websocket-client multi-mechanize matplotlib --proxy=webproxy.host.com:8080 

WORKDIR /opt/pushnotification/NOTIFICATIONS_QUEUE
EXPOSE 8889

# Define default command.
CMD /usr/local/bin/wait_for_it.sh -h $RABBITMQ_HOST -p 5672 --timeout=50 --strict -- \  
    "python NotificationServer_QUEUE.py"
