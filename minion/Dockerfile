FROM debian:latest
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get -y upgrade 
RUN apt-get -y --no-install-recommends install curl uuid-runtime
ADD minion.sh /opt/minion/minion.sh
RUN chmod 0777 /opt/minion/minion.sh

ENTRYPOINT /opt/minion/minion.sh
