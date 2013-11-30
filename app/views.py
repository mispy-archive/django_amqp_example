from django.http import HttpResponse
from amqp.connection import Connection
from amqp.channel import Channel
from amqp.basic_message import Message
import json
import socket

class RpcClient(object):
    def __init__(self):
        self.response = None

        self.connection = Connection()
        self.channel = Channel(self.connection)

        (self.queue, _, _) = self.channel.queue_declare(exclusive=True)
        self.channel.queue_bind(self.queue, exchange='django_amqp_example')

    def request(self, body):
        message = Message(
            body=json.dumps(body),
            reply_to=self.queue,
            content_type='application/json')
        
        self.channel.basic_publish(
            message,
            exchange='django_amqp_example',
            routing_key='task_queue')

        print "Task submitted:", json.dumps(body)

        def callback(msg):
            self.response = json.loads(msg.body)

        self.channel.basic_consume(
            callback=callback,
            queue=self.queue,
            no_ack=True)

        while True:
            self.connection.drain_events(timeout=60)
            if self.response is not None: 
                break

        self.connection.close()
        return self.response

def rpc(request):
    content = request.GET['msg']
    interface = RpcClient()

    try:
        response = interface.request({'content': content})
    except socket.timeout:
        return HttpResponse("Request to backend RPC server timed out", status=500)

    return HttpResponse(response['rot13'])
