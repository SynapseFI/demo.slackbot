FROM ubuntu:latest
MAINTAINER Steven Broderick "steven@synapsepay.com"
RUN apt-get install --no-install-recommends -y -q python3 python3-pip python3-dev
RUN apt-get install -y python-pip python-dev postgresql python-dev postgresql
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["gunicorn", "synapse_slackbot.run:app", "--timeout", "240"]
