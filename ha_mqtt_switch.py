# Home Assistant compatible mqtt switch
# Home Assistant
# (C) Copyright Renaud Guillon 2020.
# Released under the MIT licence.

from ha_mqtt_entity import HaMqttEntity


class HaMqttSwitch(HaMqttEntity):

    def __init__(self, name, switch):
        super().__init__(model="switch", name=name)

        self.switch = switch

        self.current_state['state'] = "OFF"

        self.discover_conf["state_topic"] = "{}/state".format(self.base_topic)
        self.discover_conf["command_topic"] = "{}/set".format(self.base_topic)
        self.discover_conf["payload_on"] = '{"state":"ON"}'
        self.discover_conf["payload_off"] = '{"state":"OFF"}'
        self.discover_conf["value_template"] = '{{ value_json.state }}'
        self.discover_conf["state_on"] = "ON"
        self.discover_conf["state_off"] = "OFF"

        self.input_topics["{}/set".format(self.base_topic)] = self.set
        self.output_topics["{}/state".format(self.base_topic)] = self.state

    def set(self, payload):
        try:
            self.current_state['state'] = payload['state']

            if self.current_state['state'] == "ON":
                self.switch.on()
            else:
                self.switch.off()

            self.is_updated = True
        except KeyError:
            pass

    def state(self):
        return self.current_state


