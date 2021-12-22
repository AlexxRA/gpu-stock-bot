FROM python:3.8-rc-slim-buster

RUN pip3 install yeelight
RUN pip3 install requests
RUN pip3 install bs4
RUN apt-get -y install python3-pandas
RUN pip3 install pandas
# COPY files/* /home/