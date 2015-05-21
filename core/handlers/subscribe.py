# -*- coding: utf-8 -*-
import json
from core.connection.rabbitmq import PikaClient
from core.connection.redis import redis_client
from core.handlers.base import BaseSockJSHandler
from chatapp.models import Message
from tornado import gen
import tornado.ioloop
import tornadoredis.pubsub


class SubscribeHandlerBase(BaseSockJSHandler):
    JOIN_MESSAGE = None
    LEAVE_MESSAGE = None

    def send_message(self, message):
        raise NotImplementedError


class TornadoSubscribeHandler(SubscribeHandlerBase):
    participants = set()

    def on_open(self, request):
        super(TornadoSubscribeHandler, self).on_open(request)
        if self.JOIN_MESSAGE:
            self.send_message(self.JOIN_MESSAGE)
        self.participants.add(self)

    @gen.coroutine
    def on_message(self, message):
        super(TornadoSubscribeHandler, self).on_message(message)
        message_id = yield Message.insert(self._message_json)
        self.send_message(message)

    def on_close(self, message=None):
        self.participants.remove(self)
        if self.LEAVE_MESSAGE:
            self.send_message(self.LEAVE_MESSAGE)

    def send_message(self, message):
        self.broadcast(self.participants, message)


class RedisSubscribeHandler(SubscribeHandlerBase):
    subscriber = tornadoredis.pubsub.SockJSSubscriber(tornadoredis.Client())
    publisher = redis_client
    CHANNEL = 'tornado'

    def on_open(self, request):
        super(RedisSubscribeHandler, self).on_open(request)
        if self.JOIN_MESSAGE:
            self.send_message(self.JOIN_MESSAGE)
        self.subscriber.subscribe(self.CHANNEL, self)

    @gen.coroutine
    def on_message(self, message):
        super(RedisSubscribeHandler, self).on_message(message)
        message_id = yield Message.insert(self._message_json)
        self.send_message(message)

    def on_close(self, message=None):
        self.subscriber.unsubscribe(self.CHANNEL, self)
        if self.LEAVE_MESSAGE:
            self.send_message(self.LEAVE_MESSAGE)

    def send_message(self, message):
        self.publisher.publish(self.CHANNEL, message)


class RabbitMQSubscribeHandler(SubscribeHandlerBase):
    CHANNEL = 'tornado'

    def on_open(self, request):
        super(RabbitMQSubscribeHandler, self).on_open(request)
        self.pika_client = PikaClient(exchange=self.CHANNEL)
        self.pika_client.websocket = self
        tornado.ioloop.IOLoop.instance().add_timeout(1, self.pika_client.connect)
        # self.send_message(self.JOIN_MESSAGE)

    @gen.coroutine
    def on_message(self, message):
        super(RabbitMQSubscribeHandler, self).on_message(message)
        message_id = yield Message.insert(self._message_json)
        self.send_message(message)

    def on_close(self, message=None):
        if self.LEAVE_MESSAGE:
            self.send_message(self.LEAVE_MESSAGE)
        self.pika_client.connection.close()

    def send_message(self, message):
        self.pika_client.sample_message(message)

    def write_message(self, message):
        """
            Only for Pika's Client!
        """
        participants = (self, )
        self.broadcast(participants, message)