from django.http import HttpResponse
from amqp.connection import Connection
from amqp.channel import Channel
from amqp.basic_message import Message
import json
import socket

class RpcClient(object):
    def __init__(self):
        self.response = None

    def request(self, body):
        connection = Connection()
        channel = Channel(connection)
        channel.exchange_declare(exchange='django_amqp_example', type='topic', auto_delete=False)
        channel.queue_declare(queue='task_queue', durable=True)

        (queue_name, _, _) = channel.queue_declare(exclusive=True)
        channel.queue_bind(queue_name, exchange='django_amqp_example')

        message = Message(
            body=json.dumps(body),
            reply_to=queue_name,
            content_type='application/json')
        
        channel.basic_publish(
            message,
            exchange='django_amqp_example',
            routing_key='task_queue')

        print "Task submitted"

        def callback(msg):
            self.response = json.loads(msg.body)

        channel.basic_consume(
            callback=callback,
            queue=queue_name,
            no_ack=True)

        while True:
            connection.drain_events(timeout=60)
            if self.response is not None: 
                break

        connection.close()
        return self.response

def rpc(request):
    content = request.GET['msg']
    interface = RpcClient()

    try:
        response = interface.request({'content': content})
    except socket.timeout:
        return HttpResponse("Request to backend RPC server timed out", status=500)

    return HttpResponse(response['rot13'])
