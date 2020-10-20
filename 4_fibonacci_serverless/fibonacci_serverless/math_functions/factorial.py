from multiprocessing.pool import ThreadPool

import requests

FACTORIAL_CHUNK_SIZE = 100


def get_factorial_value(n_value):
    return get_factorial_range(1, n_value)


def get_factorial_range(min_n, max_n):
    result = min_n
    for i in range(min_n + 1, max_n + 1):
        result *= i
    return result


def _do_factorial_request(min_n, max_n, self_hostname):
    req_url = 'https://' + self_hostname + '/factorial_parallel/%s/%s' % (
        min_n, max_n
    )
    resp = requests.get(req_url)
    if resp.status_code != 200:
        return None
    return resp.json()['result']  # may be None due to failure during recursion


def get_factorial_parallel(min_n, max_n, self_hostname):
    """
    Recursively split range in half, requesting another serverless
    container instance in a background thread, then combine results.
    """
    if max_n - min_n < FACTORIAL_CHUNK_SIZE:
        return get_factorial_range(min_n, max_n)

    mid_point = min_n + round((max_n - min_n) / 2)

    # send request to another instance and wait in a background thread
    pool = ThreadPool(processes=1)
    async_result = pool.apply_async(
        _do_factorial_request,
        (min_n, mid_point, self_hostname)
    )

    result1 = get_factorial_range(mid_point+1, max_n)
    result2 = async_result.get()

    if result2 is None:
        return None

    return result1 * result2

