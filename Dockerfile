FROM python:3.8-slim as base

WORKDIR /catalog

COPY ./ ./

RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt