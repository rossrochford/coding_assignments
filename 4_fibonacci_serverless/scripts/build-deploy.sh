#!/usr/bin/env bash

gcloud="/home/ross/code/tools/google-cloud-sdk/bin/gcloud"
export REGION="europe-west1"
docker build -t fibonacci-serverless:latest .
gcloud builds submit --tag gcr.io/$GCP_PROJECT/fibonacci-serverless
gcloud beta run deploy fibonacci-serverless --memory 2Gi --platform managed --region $REGION --image gcr.io/$GCP_PROJECT/fibonacci-serverless
