# Pull base image.
FROM debian:latest

# let's have a nice motd message
COPY assets/motd /etc/motd

# let's set the local proxy
RUN echo 'Acquire::http::Proxy "http://webproxy.bla.com:8080";' >> /etc/apt/apt.conf
RUN echo 'Acquire::https::Proxy "https://webproxy.bla.com:8080";' >> /etc/apt/apt.conf



#let's update
RUN apt-get update

#let's install the internet
RUN apt-get install -y --force-yes \
		apt-utils \ 
		supervisor \
		wget \
		htop \
		memcached\
	&& rm -rf /var/lib/apt/lists/*


#let's have also the proxy
RUN export http_proxy=webproxy.bla.com:8080
RUN export https_proxy=webproxy.bla.com:8080

# let's configure supervisor
RUN mkdir -p /var/log/supervisor /var/run/supervisor /etc/supervisor/conf.d

# let's copy the memcache config
COPY assets/memcached.conf /etc/

# let's copy the supervisor config files
COPY assets/supervisord.conf /etc/supervisor/
COPY assets/memcached_supervisor.conf /etc/supervisor/conf.d/


EXPOSE 11211

# Define default command.
CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
