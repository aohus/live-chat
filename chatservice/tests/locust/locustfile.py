from __future__ import absolute_import, print_function, unicode_literals

import json
import random
import time
import uuid

import gevent
import six
from locust import HttpUser, between, task
from websocket import create_connection


class ChatTaskUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.user_id = six.text_type(uuid.uuid4())
        ws = create_connection("ws://172.16.153.128:8000/api/v1/ws")
        self.ws = ws

        def _receive():
            while True:
                res = self.ws.recv()
                try:
                    data = json.loads(res)
                except:
                    print(res)
                end_at = time.time()
                response_time = int((end_at - data.get("timestamp")) * 1000)
                self.environment.events.request.fire(
                    request_type="WebSocket Recv",
                    name="test/ws/chat/recv",
                    response_time=response_time,
                    response_length=len(res),
                )

        gevent.spawn(_receive)

    def on_quit(self):
        self.ws.close()

    @task
    def sent(self):
        start_at = time.time()
        message = {
            "type": "send_message",
            "content": f"say something {random.random}",
            "user_id": 1,
            "timestamp": start_at,
        }
        body = json.dumps(message)

        self.ws.send(body)
        self.environment.events.request.fire(
            request_type="WebSocket Sent",
            name="test/ws/chat/send",
            response_time=int((time.time() - start_at) * 1000),
            response_length=len(body),
            exception=None,
        )
