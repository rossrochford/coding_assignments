import asyncio
import functools
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


redis_cli = redis.StrictRedis(host=REDIS_HOSTNAME, port=REDIS_PORT)
hypercorn_config = Config.from_mapping(worker_class='trio', bind='0.0.0.0:5000')


import warnings
from typing import Any, Awaitable, Callable, Coroutine, Optional, Union
import warnings
from typing import Any, Awaitable, Callable, Coroutine, Optional, Union

import trio
from hypercorn.config import Config as HyperConfig
#from hypercorn.trio import serve
from quart.logging import create_serving_logger
from hypercorn.typing import ASGIFramework
from hypercorn.trio.run import worker_serve


async def serve__with_background_task(
    app: ASGIFramework,
    config: Config,
    *,
    shutdown_trigger: Optional[Callable[..., Awaitable[None]]] = None,
    task_status: trio._core._run._TaskStatus = trio.TASK_STATUS_IGNORED,
) -> None:
    if config.debug:
        warnings.warn("The config `debug` has no affect when using serve", Warning)
    if config.workers != 1:
        warnings.warn("The config `workers` has no affect when using serve", Warning)

    serve_func = functools.partial(
        worker_serve, app, config, shutdown_trigger=shutdown_trigger, task_status=task_status
    )
    #await worker_serve(app, config, shutdown_trigger=shutdown_trigger, task_status=task_status)
    import pdb; pdb.set_trace()
    async with trio.open_nursery() as nursery:
        nursery.start_soon(serve_func)
        nursery.start_soon(forward_results_from_redis)


class QuartTrio2(QuartTrio):

    def run(  # type: ignore
        self,
        host: str = "127.0.0.1",
        port: int = 5000,
        debug: Optional[bool] = None,
        use_reloader: bool = True,
        ca_certs: Optional[str] = None,
        certfile: Optional[str] = None,
        keyfile: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        if kwargs:
            warnings.warn(
                f"Additional arguments, {','.join(kwargs.keys())}, are not supported.\n"
                "They may be supported by Hypercorn, which is the ASGI server Quart "
                "uses by default. This method is meant for development and debugging."
            )

        scheme = "https" if certfile is not None and keyfile is not None else "http"
        print(f"Running on {scheme}://{host}:{port} (CTRL + C to quit)")  # noqa: T001, T002

        trio.run(self.run_task2, host, port, debug, use_reloader, ca_certs, certfile, keyfile)

    def run_task2(
        self,
        host: str = "127.0.0.1",
        port: int = 5000,
        debug: Optional[bool] = None,
        use_reloader: bool = True,
        ca_certs: Optional[str] = None,
        certfile: Optional[str] = None,
        keyfile: Optional[str] = None,
        shutdown_trigger: Optional[Callable[..., Awaitable[None]]] = None,
    ) -> Coroutine[None, None, None]:

        config = HyperConfig()
        config.access_log_format = "%(h)s %(r)s %(s)s %(b)s %(D)s"
        config.accesslog = create_serving_logger()
        config.bind = [f"{host}:{port}"]
        config.ca_certs = ca_certs
        config.certfile = certfile
        if debug is not None:
            config.debug = debug
        config.errorlog = config.accesslog
        config.keyfile = keyfile
        config.use_reloader = use_reloader

        return serve__with_background_task(self, config)

    '''
    def run(  # type: ignore
        self,
        host: str = "127.0.0.1",
        port: int = 5000,
        debug: Optional[bool] = None,
        use_reloader: bool = True,
        ca_certs: Optional[str] = None,
        certfile: Optional[str] = None,
        keyfile: Optional[str] = None,
        **kwargs: Any,
    ) -> None:

        if kwargs:
            warnings.warn(
                f"Additional arguments, {','.join(kwargs.keys())}, are not supported.\n"
                "They may be supported by Hypercorn, which is the ASGI server Quart "
                "uses by default. This method is meant for development and debugging."
            )

        scheme = "https" if certfile is not None and keyfile is not None else "http"
        print(f"Running on {scheme}://{host}:{port} (CTRL + C to quit)")  # noqa: T001, T002

        # a little hacky
        run_task = functools.partial(
            self.run_task,
            host, port, debug, use_reloader,
            ca_certs, certfile, keyfile
        )
        run_task2 = self._run_with_background_task(run_task)
        #trio.run(task, host, port, debug, use_reloader, ca_certs, certfile, keyfile)
        trio.run(run_task2)

    async def _run_with_background_task(self, main_run_task):
        warnings.warn('running background task')
        async with trio.open_nursery() as nursery:
            #nursery.start_soon(main_run_task)
            nursery.start_soon(forward_results_from_redis)
    '''


app = QuartTrio(__name__)
app.SUBSCRIBER_CHANNELS = set()  # local queues for each subscribing websocket client


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
    app.SUBSCRIBER_CHANNELS.add(send_channel)

    try:
        async with send_channel, receive_channel:
            async for message in receive_channel:
                await websocket.send(message)
    except trio.Cancelled:
        pass

    app.SUBSCRIBER_CHANNELS.remove(send_channel)


async def forward_results_from_redis(config, nursery):
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
            # cancellable so hypercorn/trio can clean up
            iterator.__next__, cancellable=True
        )

        if item['type'] != 'message':
            continue
        result_str = item['data'].decode()

        # send result to subscribers
        to_remove = []
        for channel in app.SUBSCRIBER_CHANNELS:
            if channel._closed:
                to_remove.append(channel)
                continue
            await channel.send(result_str)

        # remove channels of disconnected websockets
        for channel in to_remove:
            app.SUBSCRIBER_CHANNELS.remove(channel)


@app.before_serving
async def launch_background_tasks():
    app.nursery.start_soon(forward_results_from_redis, None, app.nursery)


'''
async def main():
    """ launch webserver and redis-notify worker"""
    async with trio.open_nursery() as nursery:
        nursery.start_soon(hypercorn_serve, app, hypercorn_config)
        nursery.start_soon(forward_results_from_redis, hypercorn_config, nursery)


if __name__ == '__main__':
    trio.run(main)
'''