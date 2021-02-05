# Home Assistant mqtt integration
# (C) Copyright Renaud Guillon 202.
# Released under the MIT licence.

import json

try:
    import asyncio
except ImportError:
    import uasyncio as asyncio

import ha_mqtt

# default root topic for home assistant discovery
HOME_ASSISTANT_PREFIX = "homeassistant"


class HaMqttEntity(object):
    '''
    Base class for Home Assistant Mqtt Entities, the implementations are expected to populate the discover_conf with
    the parameters specific to the device type, and input_topics/output_topics that are dictionaries of mqtt topic/
    callback.
    The service on_connect will subscribe to every input topics and send the mqtt discovery message to Home assistant.
    A task will be created to monitor is_updated, if true, the output_topics are published, to inform home assistant of
    the new state of the entity

    TODO: json payload management here is not the best idea as many kinds of devices uses other format by default
    '''
    def __init__(self, model, name):
        self.base_topic = "{}/{}/{}".format(HOME_ASSISTANT_PREFIX, model, name)
        self.discover_topic = bytes("{}/config".format(self.base_topic), 'utf-8')
        self.discover_conf = {"name": name,
""                            "unique_id": bytes("{}_{}".format(model, name), 'utf-8')}
        self.input_topics = {}
        self.output_topics = {}

        self.current_state = {}
        self.is_updated = False

        self.mqtt_client = ha_mqtt.add_entity(self)

        asyncio.get_event_loop().create_task(self.task())

    async def task(self):
        '''
        Never ending task that will send the updated state to home assistant when needed.
        '''
        while True:
            if self.is_updated:
                self.is_updated = False
                await self.update_state()
            await asyncio.sleep(0.1)

    async def update_state(self):
        for output_topic, callback in self.output_topics.items():
            await self.mqtt_client.publish(output_topic,  json.dumps(callback()))

    async def on_connect(self):
        '''
        Subscribes to every input topics and sends the mqtt discover message
        '''
        for input_topic in self.input_topics:
            await self.mqtt_client.subscribe(input_topic)
        await self.mqtt_client.publish(self.discover_topic, json.dumps(self.discover_conf))

    def receive(self, topic, message):
        '''
        Sends the message to the callback if the topic matches
        :param topic:
        :param message:
        '''
        try:
            payload = json.loads(message.decode('utf-8'))
            self.input_topics[topic.decode('utf-8')](payload)
            self.is_updated = True
        except KeyError:
            pass
