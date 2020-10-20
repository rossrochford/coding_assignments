#!/usr/bin/env bash

# python $HUEY_CONSUMER_PATH fibonacci_serverless.main.huey_cli -w3 &
export SELF_HOSTNAME=$(gcloud beta run services describe fibonacci-serverless --platform managed --region europe-west1 | sed -n 2p)
python fibonacci_serverless/main.py