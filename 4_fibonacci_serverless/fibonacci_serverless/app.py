from flask import Flask
# from huey import SqliteHuey


app = Flask(__name__)

# huey_cli = SqliteHuey()
# huey_cli = SqliteHuey(filename='/dev/shm/demo.db')

# docker build -t sample-flask-example:latest .; gcloud builds submit --tag gcr.io/skilled-boulder-257701/sample-flask-example; gcloud beta run deploy sample-flask-example --memory 2Gi --platform managed --image gcr.io/skilled-boulder-257701/sample-flask-example

# gcloud beta run services list --platform managed

# gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=sample-flask-example" --project skilled-boulder-257701 --limit 10


# python $HUEY_CONSUMER_PATH fibonacci_serverless.main.huey_cli -w4