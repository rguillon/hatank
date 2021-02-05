# Home Assistant mqtt integration
# (C) Copyright Renaud Guillon 202.
# Released under the MIT licence.
#
# Heavily inspired from Peter Hinch's clean.py example
# https://github.com/peterhinch/micropython-mqtt/tree/master/mqtt_as

from mqtt_as import MQTTClient, config
from config import wifi_led, blue_led  # Local definitions

try:
    import asyncio
except ImportError:
    import uasyncio as asyncio

mqtt_entities = []


# Subscription callback
def sub_cb(topic, msg, retained):
    for entity in mqtt_entities:
        entity.receive(topic, msg)

# Demonstrate scheduler is operational.
async def heartbeat():
    s = True
    while True:
        await asyncio.sleep_ms(500)
        blue_led(s)
        s = not s


async def wifi_han(state):
    wifi_led(not state)
    print('Wifi is ', 'up' if state else 'down')
    await asyncio.sleep(1)


# If you connect with clean_session True, must re-subscribe (MQTT spec 3.1.2.4)
async def conn_han(client):
    for entity in mqtt_entities:
        await entity.on_connect()

async def main(client):
    try:
        await client.connect()
    except OSError:
        print('Connection failed.')
        return
    while True:
        await asyncio.sleep(5)


# Define configuration
config['subs_cb'] = sub_cb
config['wifi_coro'] = wifi_han
config['connect_coro'] = conn_han
config['clean'] = True

# Set up client
mqtt_client = MQTTClient(config)

loop = asyncio.get_event_loop()
loop.create_task(heartbeat())
loop.create_task(main(mqtt_client))


def add_entity(entity):
    mqtt_entities.append(entity)
    return mqtt_client


def close_client():
    mqtt_client.close()
