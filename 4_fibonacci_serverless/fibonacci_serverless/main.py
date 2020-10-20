import os
import sys

from waitress import serve

from fibonacci_serverless.app import app
#from fibonacci_serverless.app import huey_cli
#import fibonacci_serverless.tasks  # Import tasks so they are registered with Huey instance.
#from fibonacci_serverless import views  # Import views so they are registered with Flask app.
from fibonacci_serverless.views.math_views import math_blueprint

# tasks must be imported here for workers to find them
#from fibonacci_serverless.tasks import *


app.register_blueprint(math_blueprint)

FIBONACCI_RUN_ENV = os.environ.get('FIBONACCI_RUN_ENV')
PORT = int(os.environ.get('PORT', 8080))


if __name__ == '__main__':
    # ackermann function requires high recursion limit
    sys.setrecursionlimit(9999)

    if FIBONACCI_RUN_ENV == 'dev':
        app.run(debug=False, host='0.0.0.0', port=PORT)
    elif FIBONACCI_RUN_ENV == 'prod':
        serve(app, host='0.0.0.0', port=PORT)
    else:
        exit('unexpected value for FIBONACCI_RUN_ENV: %s' % FIBONACCI_RUN_ENV)
