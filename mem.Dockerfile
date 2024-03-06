# Pull base image.
FROM base-image.dock.com/ubuntu/18.04/rel-2018w43

# let's have a nice motd message
COPY DOCKER/X64/docker_memcached/assets/motd /etc/motd

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
		memcached\
	&& rm -rf /var/lib/apt/lists/*


#let's have also the proxy
RUN export http_proxy=proxy.host.com:8080
RUN export https_proxy=proxy.host.com:8080

# let's configure supervisor
RUN mkdir -p /var/log/supervisor /var/run/supervisor /etc/supervisor/conf.d

# let's copy the memcache config
COPY DOCKER/X64/docker_memcached/assets/memcached.conf /etc/

# let's copy the supervisor config files
COPY DOCKER/X64/docker_memcached/assets/supervisord.conf /etc/supervisor/
COPY DOCKER/X64/docker_memcached/assets/memcached_supervisor.conf /etc/supervisor/conf.d/


EXPOSE 11211

# Define default command.
CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]


