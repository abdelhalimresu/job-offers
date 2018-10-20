FROM python:3.6

RUN mkdir /src
WORKDIR /src
ADD . /src
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5000
