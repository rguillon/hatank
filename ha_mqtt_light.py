# Home Assistant mqtt integration
# (C) Copyright Renaud Guillon 202.
# Released under the MIT licence.
import time

from ha_mqtt_entity import HaMqttEntity

try:
    import asyncio
except ImportError:
    import uasyncio as asyncio


class HaMqttBasicLight(HaMqttEntity):

    def __init__(self, name, light):
        super().__init__(model="light", name=name)

        self.light = light

        self.current_state['state'] = "OFF"

        self.discover_conf["state_topic"] = "{}/state".format(self.base_topic)
        self.discover_conf["command_topic"] = "{}/set".format(self.base_topic)
        self.input_topics["{}/set".format(self.base_topic)] = self.set
        self.output_topics["{}/state".format(self.base_topic)] = self.state

    def set(self, payload):
        try:
            self.current_state['state'] = payload['state']
            if self.current_state['state'] == "ON":
                self.light.on()
            else:
                self.light.off()

            self.is_updated = True
        except KeyError:
            pass

    def state(self):
        return self.current_state


class HaMqttBrightnessLight(HaMqttBasicLight):

    def __init__(self, name, light):
        super().__init__(name=name, light=light)
        self.discover_conf["brightness"] = True
        self.current_state['brightness'] = 0

    def set_brightness(self, value):
        self.current_state['brightness'] = value
        self.light.brightness(value)
        self.is_updated = True

    def set(self, payload):
        super().set(payload)
        try:
            asyncio.get_event_loop().create_task(self.brightness_task(transition=payload['transition'] * 1000,
                                                                      start_brightness=self.current_state['brightness'],
                                                                      target_brightness=payload['brightness']))
        except KeyError:
            try:
                self.set_brightness(payload['brightness'])
            except KeyError:
                pass

    async def brightness_task(self, transition, start_brightness, target_brightness):
        start_time = time.ticks_ms()
        transition_time = 0
        while transition_time < transition:
            await asyncio.sleep(1)
            self.set_brightness(
                start_brightness + transition_time * (target_brightness - start_brightness) / transition)
            transition_time = time.ticks_ms() - start_time

        self.set_brightness(target_brightness)


class HaMqttRgbLight(HaMqttBrightnessLight):

    def __init__(self, name, light):
        super().__init__(name=name, light=light)
        self.discover_conf["rgb"] = True
        self.current_state['color'] = {'r': 0, 'g': 0, 'b': 0}

    def set(self, payload):
        super().set(payload)
        try:
            asyncio.get_event_loop().create_task(self.color_task(transition=payload['transition'] * 1000,
                                                                 start_color=self.current_state['color'],
                                                                 target_color=payload['color']))
        except KeyError:
            try:
                self.set_color(payload['color'])
            except KeyError:
                pass

    def state(self):
        return self.current_state

    def set_color(self, value):
        self.current_state['color'] = value
        self.light.color(self.current_state['color'])
        self.is_updated = True

    async def color_task(self, transition, start_color, target_color):
        start_time = time.ticks_ms()
        transition_time = 0
        while transition_time < transition:
            await asyncio.sleep(1)
            c = {}
            for color in 'r', 'g', 'b':
                c[color] = start_color[color] + transition_time * (
                            target_color[color] - start_color[color]) / transition
            self.set_color(c)
            transition_time = time.ticks_ms() - start_time
        self.set_color(target_color)
