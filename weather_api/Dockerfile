FROM python:3.10-slim

RUN apt-get update && apt-get install curl -y
RUN pip install --no-cache-dir pipenv

# add unpriviliged user
RUN useradd --create-home app
USER app
WORKDIR /home/app

# install dependencies
COPY Pipfile Pipfile.lock ./
RUN pipenv sync

COPY ./main.py ./
COPY ./rdu-weather-history.json ./

ARG API_PORT
ENV HTTP_PORT=$API_PORT
EXPOSE $API_PORT
CMD [ "pipenv", "run", "python", "-u", "main.py" ]
