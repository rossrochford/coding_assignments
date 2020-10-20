
# todo: this should be calculated based on Google Cloud Run's 2GB memory limit
ACKERMANN_CACHE_LIMIT = 999999


def get_ackermann_value(m_value, n_value, cache=None):
    if cache is None:
        cache = {}

    if m_value < 0 or n_value < 0:
        return 0  # should never get here?

    if m_value == 0:
        return n_value + 1

    if (m_value, n_value) in cache:
        return cache[(m_value, n_value)]

    if n_value == 0:
        result = get_ackermann_value(m_value-1, 1, cache)
        if len(cache) < ACKERMANN_CACHE_LIMIT:
            cache[(m_value, n_value)] = result
        return result

    result = get_ackermann_value(
        m_value-1,
        get_ackermann_value(m_value, n_value-1, cache),
        cache
    )
    if len(cache) < ACKERMANN_CACHE_LIMIT:
        cache[(m_value, n_value)] = result
    return result
