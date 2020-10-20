import asyncio
import json
import os
import uuid

import redis
import trio
from hypercorn.config import Config
from hypercorn.trio import serve as hypercorn_serve
from quart import Quart, websocket
from quart_trio import QuartTrio

from power_simulator.redis_util import redis__queue_push, redis__wait_for_key


REDIS_HOSTNAME = os.environ.get('REDIS_HOSTNAME', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))

WORKER_QUEUE = 'gs_worker_queue'
WS_NOTIFY_KEY = 'gs_ws_notify_key'
SIMULATION_RESULT_KEY = 'simulation-result'

SUBSCRIBER_CHANNELS = set()  # local queues for each subscribing websocket client

app = QuartTrio(__name__)

redis_cli = redis.StrictRedis(host=REDIS_HOSTNAME, port=REDIS_PORT)
hypercorn_config = Config.from_mapping(worker_class='trio', bind='0.0.0.0:5000')


async def _do_background_task(redis_cli, task_uid, task_type, task_kwargs):

    # push task to worker queue
    wait_key = 'wait-' + task_uid + uuid.uuid4().hex[:6]
    msg = json.dumps({
        'task_type': task_type,
        'task_kwargs': task_kwargs,
        'redis_resultkey': task_uid,
        'redis_waitkey': wait_key
    })
    await trio.to_thread.run_sync(
        redis__queue_push, redis_cli, WORKER_QUEUE, msg
    )

    # block for wait_key and fetch result
    await trio.to_thread.run_sync(
        redis__wait_for_key, redis_cli, wait_key
    )
    result = await trio.to_thread.run_sync(
        redis_cli.hmget, task_uid, 'task_result'
    )
    return result[0].decode()


@app.route('/run-simulation', methods=['POST'])
async def run_simulation_view():
    """
    Runs simulation as a background task, publishes
    to WS_NOTIFY_KEY when complete.
    """
    result_json_str = await _do_background_task(
        redis_cli, SIMULATION_RESULT_KEY, 'run-simulation', None
    )

    # publish to redis/WS_NOTIFY_KEY
    await trio.to_thread.run_sync(
        redis_cli.publish, WS_NOTIFY_KEY, result_json_str
    )

    return json.loads(result_json_str)


async def _get_cached_value(field_key):
    result = await trio.to_thread.run_sync(
        redis_cli.hmget, SIMULATION_RESULT_KEY, 'task_result'
    )
    if result[0] is None:
        return 'no-cached-value'

    result_dict = json.loads(result[0].decode())
    return str(result_dict[field_key])


@app.route('/active-power', methods=['GET'])
async def get_cached_active_power():
    return await _get_cached_value('active_power')


@app.route('/reactive-power', methods=['GET'])
async def get_cached_reactive_power():
    return await _get_cached_value('reactive_power')


@app.websocket('/simulator-subscribe')
async def simulator_websocket_subscribe():
    """
    Accepts connections, opens a trio send/receive channel pair,
    waits for results and forwards them to the websocket client
    """

    await websocket.send_json({'status': 'subscribed'})

    send_channel, receive_channel = trio.open_memory_channel(10)

    try:
        async with send_channel, receive_channel:
            SUBSCRIBER_CHANNELS.add(send_channel)
            async for message in receive_channel:
                await websocket.send(message)
    except asyncio.CancelledError:
        # NOTE: websocket disconnection isn't working
        print('disconnected')

    SUBSCRIBER_CHANNELS.remove(send_channel)


async def forward_results_from_redis():
    """
    Forwards results from Redis/WS_NOTIFY_KEY to local/SUBSCRIBER_CHANNELS
    """
    def _get_pubsub_iter(redis_cli, key):
        p = redis_cli.pubsub()
        p.subscribe(key)
        return p.listen().__iter__()

    iterator = await trio.to_thread.run_sync(
        _get_pubsub_iter, redis_cli, WS_NOTIFY_KEY
    )

    while True:
        item = await trio.to_thread.run_sync(
            iterator.__next__
        )
        if item['type'] != 'message':
            continue
        result_str = item['data'].decode()

        # send result to subscribers
        for channel in SUBSCRIBER_CHANNELS:
            await channel.send(result_str)


async def main():
    """ launch webserver and redis-notify worker"""

    async with trio.open_nursery() as nursery:
        nursery.start_soon(hypercorn_serve, app, hypercorn_config)
        nursery.start_soon(forward_results_from_redis)


if __name__ == '__main__':
    trio.run(main)
