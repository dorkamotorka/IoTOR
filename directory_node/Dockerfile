FROM python:3.10-slim
RUN pip install --no-cache-dir pipenv
RUN apt-get update && apt-get install curl -y

# add unpriviliged user
RUN useradd --create-home app
USER app
WORKDIR /home/app

# install dependencies
COPY Pipfile Pipfile.lock ./
RUN pipenv sync

# copy app
COPY project ./project/
COPY app.py ./

EXPOSE 5000
CMD ["pipenv", "run", "flask", "--app", "app", "run", "--host", "0.0.0.0"]
