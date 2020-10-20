# Use the official Python 3 image.
# https://hub.docker.com/_/python
#
# python:3 builds a 954 MB image - 342.3 MB in Google Container Registry
# FROM python:3
#
# python:3-slim builds a 162 MB image - 51.6 MB in Google Container Registry
# FROM python:3-slim
#
# python:3-alpine builds a 97 MB image - 33.2 MB in Google Container Registry
FROM python:3-alpine

# RUN apt-get update -y
# RUN apt-get install -y python-pip

COPY . /app

# Create and change to the app directory.
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH /app

RUN chmod 444 fibonacci_serverless/app.py
RUN chmod 444 requirements.txt
RUN chmod +x docker_cmd.sh

#RUN mkdir /app/tmp
#USER root
#RUN su root -c "mount -t tmpfs -o size=32m tmpfs /app/tmp"

#RUN touch /app/demo.db
#RUN chmod +w /app/demo.db

# Service must listen to $PORT environment variable.
# This default value facilitates local development.
ENV PORT 8080
ENV FIBONACCI_RUN_ENV=prod
#ENV HUEY_CONSUMER_PATH /usr/local/lib/python3.8/site-packages/huey/bin/huey_consumer.py

# Run the web service on container startup.
CMD ["python", "fibonacci_serverless/main.py"]
#CMD [ "sh", "/app/docker_cmd.sh" ]
