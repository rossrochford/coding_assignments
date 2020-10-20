import logging

from flask import Blueprint
from flask import Flask, abort, jsonify, request
import tldextract

from fibonacci_serverless.math_functions.ackermann import get_ackermann_value
from fibonacci_serverless.math_functions.factorial import get_factorial_value, get_factorial_parallel
from fibonacci_serverless.math_functions.fibonacci import get_fibonacci_value


math_blueprint = Blueprint('math_routes', __name__)

FACTORIAL_CHUNK_SIZE = 20

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('cloudrun-flask')


def create_result_html(page_title, result):
    html = """<html><title>%s</title><body><p>Result: %s</p></html>"""
    return html % (page_title, result)


@math_blueprint.route('/home')
def home():
    msg = request.base_url
    return create_result_html('Homepage', msg)


@math_blueprint.route('/ackermann/<int:m_value>/<int:n_value>', methods=['GET'])
def ackermann(m_value, n_value):
    if m_value < 0 or n_value < 0:
        abort(400, 'ackermann input values must be >= 0')
    result = get_ackermann_value(m_value, n_value)
    return create_result_html('Ackermann result', result)


@math_blueprint.route('/factorial/<int:input_value>/', methods=['GET'])
def factorial(input_value):

    if input_value <= 0:
        abort(400, 'factorial input must be >= 1')
    result = get_factorial_value(input_value)
    return create_result_html('Factorial result', result)


@math_blueprint.route(
    '/factorial_parallel/<int:max_value>', defaults={'min_value': 1}, methods=['GET']
)
@math_blueprint.route('/factorial_parallel/<int:min_value>/<int:max_value>/', methods=['GET'])
def factorial_parallel(min_value, max_value):
    if max_value <= 0:
        abort(400, 'factorial input must be >= 1')

    tld = tldextract.extract(request.base_url)
    self_hostname = '%s.%s.%s' % (tld.subdomain, tld.domain, tld.suffix)

    result = get_factorial_parallel(
        min_value, max_value, self_hostname
    )
    if result is None:
        return jsonify({'result': None, 'status': 'failed'})

    return jsonify({'result': result, 'status': 'success'})


@math_blueprint.route('/fibonacci/<int:input_value>/', methods=['GET'])
def fibonacci(input_value):
    if input_value < 0:
        abort(400, 'fibonacci input must be >= 0')
    result = get_fibonacci_value(input_value)
    return create_result_html('Fibonacci result', result)




