#!/usr/bin/env python

from amqp.connection import Connection
from amqp.channel import Channel
from amqp.basic_message import Message
import json

connection = Connection()
channel = Channel(connection)

channel.exchange_declare('django_amqp_example', 'topic', auto_delete=False)
channel.queue_declare(queue='task_queue', durable=True)
channel.queue_bind('task_queue', 'django_amqp_example', 'task_queue')

def callback(msg):
    print "Received request:", msg.body
    content = json.loads(msg.body)['content']
    response = {
        'rot13': content.encode('rot13')
    }

    response_msg = Message(
        body=json.dumps(response),
        exchange='django_amqp_example')

    print "Sending response:", json.dumps(response)
    channel.basic_publish(
        response_msg,
        routing_key=msg.reply_to)

channel.basic_consume(callback=callback, queue='task_queue')

print "Worker is waiting for requests"
while True:
    connection.drain_events()
