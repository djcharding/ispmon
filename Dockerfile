FROM ubuntu
RUN apt-get update
RUN apt-get install gnupg1 apt-transport-https dirmngr lsb-release -y && \
    export INSTALL_KEY=379CE192D401AB61 && \
    export DEB_DISTRO=$(lsb_release -sc) && \
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys $INSTALL_KEY && \
    echo "deb https://ookla.bintray.com/debian ${DEB_DISTRO} main" | tee  /etc/apt/sources.list.d/speedtest.list 
RUN apt-get update && \
    apt-get install speedtest -y
RUN apt-get install python3.6 python3-pip -y
RUN mkdir /app/
ADD requirements.txt /app/
WORKDIR /app
RUN pip3 install -r requirements.txt
RUN export PATH=”$PATH:/usr/local/bin/python
