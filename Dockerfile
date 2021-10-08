FROM python:3.6.14-alpine3.13
# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache gcc musl-dev libxslt-dev && pip3 install pip==20.2.4

COPY ./requirements.txt /usr/src/app/requirements.txt

RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/app/
