# start with a base image
# FROM ubuntu:16.04
FROM python:3.4-slim

# install dependencies
RUN apt-get update && apt-get install -y \
apt-utils \
build-essential \
nginx \
libpq-dev \
supervisor \
python3-pip \
python3-dev \
git \
&& rm -rf /var/lib/apt/lists/*

RUN echo "America/New_York" > /etc/timezone; dpkg-reconfigure -f noninteractive tzdata

# update working directories
COPY ./app /app
COPY ./config /config
COPY requirements.txt /

# install dependencies
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt

# install brotli
#RUN git clone https://github.com/indygreg/python-zstandard.git \
# && cd python-zstandard \
#    && python setup.py build_ext

RUN groupadd -r swuser -g 433 && \
useradd -u 431 -r -g swuser -d /app -s /sbin/nologin -c "Docker image user" swuser && \
chown -R swuser:swuser /app

# setup config
RUN echo "\ndaemon off;" >> /etc/nginx/nginx.conf
RUN rm /etc/nginx/sites-enabled/default

RUN ln -s /config/nginx.conf /etc/nginx/sites-enabled/
RUN ln -s /config/supervisor.conf /etc/supervisor/conf.d/

EXPOSE 80
CMD ["supervisord", "-n"]
