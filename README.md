# django\_amqp\_example

This is an example of using Django as an asynchronous HTTP frontend to a more complex system, similar to the way nodejs is often used. It takes a query from the browser and holds the connection open while it waits for the message to be processed over AMQP, using gevent to prevent locking of the process.

Requires [Python 2.7.3+](http://www.python.org/download/releases/2.7.3/) and the [pip](https://pypi.python.org/pypi/pip) package manager

## Running the example

1. Clone the repository
2. `pip install -r requirements.pip`
3. Start the backend AMQP consumer: `python worker.py`
4. Start the gevent-backed webserver: `gunicorn app.wsgi:application -c gunicorn.conf.py --debug --log-level debug`

Now go to `http://localhost:800/rpc?msg=secrets` and you should receive the appropriate rot13 response from `worker.py` :)
