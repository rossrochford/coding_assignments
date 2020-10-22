#!/bin/bash

export PYTHONPATH=$(pwd)


python power_simulator/background_worker.py &
pid[0]=$!


python power_simulator/webserver.py &
#hypercorn --bind "0.0.0.0:5000" --worker-class trio --workers 1 --websocket-ping-interval 3 power_simulator/webserver.py &
pid[1]=$!

trap "kill ${pid[0]} ${pid[1]}; exit 1" INT
wait
