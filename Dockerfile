FROM ubuntu:14.04

RUN apt-get update \
    && apt-get install -y tar git curl nano wget dialog net-tools build-essential \
    && apt-get install --no-install-recommends -y -q python3 python3-pip python3-dev \
    && apt-get install -y libxml2-dev libxslt-dev python-dev zlib1g-dev postgresql
ADD . /bot
WORKDIR /bot
RUN pip3 install -r requirements.txt
 
# Expose port 8000
EXPOSE 8000

ENTRYPOINT ["gunicorn", "synapse_slackbot.run:app", "--timeout", "240"]
