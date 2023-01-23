FROM python:3.10-slim

RUN apt-get update && apt-get install curl -y
RUN pip3 install pipenv

ENV PROJECT_DIR /usr/src/chain_api

WORKDIR ${PROJECT_DIR}

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv install --deploy --ignore-pipfile

COPY . .

ARG CHAIN_PORT
EXPOSE $CHAIN_PORT

ENV BIND_HOST 0.0.0.0
ENTRYPOINT ["pipenv", "run", "python", "-u", "wsgi.py"]
