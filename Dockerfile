FROM ubuntu:latest
MAINTAINER Steven Broderick "steven@synapsepay.com"
RUN apt-get update -y
# common dependencies
RUN apt-get install --no-install-recommends -y -q build-essential apt-utils autoconf libtool pkg-config python-opengl python-imaging python-pyrex python-pyside.qtopengl idle-python2.7 qt4-dev-tools qt4-designer libqtgui4 libqtcore4 libqt4-xml libqt4-test libqt4-script libqt4-network libqt4-dbus python-qt4 python-qt4-gl libgle3
# python dependencies
RUN apt-get install --no-install-recommends -y -q python python-pip python-dev python3 python3-pip python3-dev libpq-dev
COPY . /app
WORKDIR /app
RUN pip3 install --upgrade pip
RUN pip3 install setuptools
RUN pip3 install -r requirements.txt
ENTRYPOINT ["gunicorn", "synapse_slackbot.run:app", "--timeout", "240"]
