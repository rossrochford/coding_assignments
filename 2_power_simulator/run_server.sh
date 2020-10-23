#!/bin/bash

export PYTHONPATH=$(pwd)


python power_simulator/background_worker.py &
pid[0]=$!


hypercorn --bind "0.0.0.0:5000" --worker-class trio --workers 2 --websocket-ping-interval 3 power_simulator/webserver.py &
pid[1]=$!

trap "kill ${pid[0]} ${pid[1]}; exit 1" INT
wait
