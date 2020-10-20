from collections import defaultdict
import datetime
import json
import logging
import os
import sys
import time

import requests

TIMEOUT = 10
EXPECTED_STATUS = 200
MAX_HISTORY_SIZE = 10

LOG_FILEPATH = os.environ.get(
    'HEALTH_CHECK_LOG_FILEPATH', (os.getcwd() + '/health-check.log')
)


def create_filelogger():
    logger = logging.getLogger('healthcheck_daemon')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(LOG_FILEPATH)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    return logger


logger = create_filelogger()


def get_timestamp_string():
    now = datetime.datetime.utcnow()
    return now.isoformat().split('.')[0]


def _do_health_check(http_session, endpoint_url):
    """ Attempt request at endpoint, return slug describing result"""
    try:
        resp = http_session.get(endpoint_url, timeout=TIMEOUT)
        if resp.status_code == EXPECTED_STATUS:
            return 'healthy'

        return f"unexpected-status-{resp.status_code}"

    except requests.exceptions.Timeout:
        return 'request-timeout'
    except requests.exceptions.RequestException:
        return 'unexpected-request-exception'


def _log_health_check_history(endpoint_url, health_check_history):
    """ write summary of recent health checks to log"""

    del health_check_history['history_size']

    num_healthy, num_unhealthy = 0, 0
    for check_type, timestamps in health_check_history.items():
        if check_type == 'healthy':
            num_healthy = len(timestamps)
        else:
            num_unhealthy += len(timestamps)

    health_check_history['num_healthy'] = num_healthy
    health_check_history['num_unhealthy'] = num_unhealthy

    history_json = json.dumps(health_check_history)
    logger.info(
        f"health check summary for {endpoint_url}: {history_json}"
    )


def _log_health_check(endpoint_url, check_result, health_check_history):
    """ Store record of health check in health_check_history and write line to log file"""

    health_check_history[check_result].append(
        get_timestamp_string()
    )
    health_check_history['history_size'] += 1

    if check_result == 'healthy':
        logger.info(f"{endpoint_url} is healthy")
    else:
        logger.error(f"{endpoint_url} failed: {check_result}")

    if health_check_history['history_size'] > MAX_HISTORY_SIZE:
        _log_health_check_history(endpoint_url, health_check_history)
        health_check_history.clear()  # flush history
        health_check_history['history_size'] = 0


def health_monitor_daemon(endpoint_url, interval):

    health_check_history = defaultdict(list)
    health_check_history['history_size'] = 0

    http_session = requests.Session()

    while True:
        time.sleep(interval)

        health_check_result = _do_health_check(http_session, endpoint_url)

        _log_health_check(
            endpoint_url, health_check_result, health_check_history
        )


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 2:
        exit('error: expected 2 arguments: <url_endpoint> <interval>')

    endpoint = args[0]
    interval_seconds = int(args[1])
    health_monitor_daemon(endpoint, interval_seconds)
