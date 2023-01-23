FROM python:3.10-slim
RUN pip install --no-cache-dir pipenv
RUN apt-get update && apt-get install curl -y

RUN useradd --create-home app
USER app
WORKDIR /home/app

COPY Pipfile Pipfile.lock ./
RUN pipenv sync

COPY project ./project/
COPY app.py ./

EXPOSE 5001
CMD ["pipenv", "run", "flask", "--app", "app", "run", "--host", "0.0.0.0", "--port", "5001"]
