import uuid


def redis__queue_pop(redis_cli, queue_name, temp_list=None):

    if temp_list is None:
        temp_list = 'wrk-' + queue_name + uuid.uuid4().hex[:6]

    redis_cli.brpoplpush(queue_name, temp_list)
    _, body = redis_cli.blpop([temp_list])

    return body


def redis__queue_push(redis_cli, queue_name, msg_str):
    redis_cli.lpush(queue_name, msg_str)


def redis__wait_for_key(redis_cli, key):
    # this can be tested by running:
    #    redis-cli SET stash:silence/bob2 someValue

    redis_key = '__keyspace@*:' + key

    pubsub = redis_cli.pubsub()
    pubsub.psubscribe(redis_key)

    for msg in pubsub.listen():
        if msg['pattern'] is None:
            continue
        pattern, event_type = msg['pattern'].decode(), msg['data'].decode()
        if event_type != 'set':  # usually 'expire' or 'expired'
            continue
        return None


def redis__set_waitkey(redis_cli, key, value='1', key_expiry=90):
    if key_expiry is None:
        redis_cli.set(key, value)
    else:
        # key gets deleted 90s later
        redis_cli.setex(key, key_expiry, value)
