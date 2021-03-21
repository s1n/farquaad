FROM ubuntu:latest

WORKDIR /docker/

ADD . /docker

RUN apt-get update -y
# selenium requirements
RUN apt-get install -y firefox xvfb
# pip requirements
RUN apt-get install -y python3-pip git
RUN pip3 install -U setuptools setuptools_scm wheel
RUN pip3 install -r docs/requirements.txt
RUN pip3 install pyvirtualdisplay
RUN pip3 install webdrivermanager
RUN webdrivermanager firefox --linkpath /usr/local/bin
RUN pip3 install .

ADD src /docker

#CMD farquaad --help
ENTRYPOINT ["farquaad"]
CMD ["--help"]