FROM ubuntu:20.04

ENV DEBIAN_FRONTEND="noninteractive" TZ="America/New_York"
RUN apt-get update && apt-get -y install python3 tzdata python3-pip python-dev git vim locales openssh-server 

RUN pip install --upgrade pip
RUN pip install setuptools
RUN pip install numpy
RUN pip install sklearn
RUN pip install flask
RUN pip install pandas
RUN pip install scikit-surprise
RUN mkdir -p /workspace
WORKDIR /workspace
COPY . /workspace

EXPOSE 8081
CMD ["python3", "./flask_7004.py"]
