# Pull base image.
FROM debian:latest

# let's have a nice motd message
COPY assets/motd /etc/motd

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



# let's make the opt dir

RUN mkdir -p /opt/hpcmock/

# let's copy the mock

COPY assets/hpcmock /opt/hpcmock

# let's install python dependencies list
RUN pip install requests requests-oauthlib requests-toolbelt --proxy=webproxy.host.com:8080 

WORKDIR /opt/hpcmock
EXPOSE 8081

# Define default command.
CMD ["python" ,"http_server.py"]
