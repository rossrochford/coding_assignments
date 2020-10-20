import json
import os
import uuid

import redis

from power_simulator.redis_util import redis__set_waitkey
from power_simulator.test_sim import run_simulation


WORKER_QUEUE = 'gs_worker_queue'
REDIS_WORKER_LIST = 'wrk-' + WORKER_QUEUE + uuid.uuid4().hex[:6]  # unique per worker process

REDIS_HOSTNAME = os.environ.get('REDIS_HOSTNAME', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))


def task__run_simulation(redis_cli, msg):
    """ run simulation, save result to redis and set key notification"""
    active_power, reactive_power = run_simulation()

    result = {'active_power': active_power, 'reactive_power': reactive_power}

    redis_cli.hset(
        msg['redis_resultkey'],
        mapping={'task_result': json.dumps(result).encode()}
    )
    redis__set_waitkey(redis_cli, msg['redis_waitkey'])


def worker_loop():

    redis_cli = redis.StrictRedis(host=REDIS_HOSTNAME, port=REDIS_PORT)

    while True:
        redis_cli.brpoplpush(WORKER_QUEUE, REDIS_WORKER_LIST)
        _, body = redis_cli.blpop([REDIS_WORKER_LIST])

        message = json.loads(body)

        task_type = message.get('task_type')
        if task_type not in ('run-simulation',):
            print('error: task_type missing or unexpected value: %s' % task_type)
            continue

        if task_type == 'run-simulation':
            task__run_simulation(redis_cli, message)


if __name__ == '__main__':
    worker_loop()
