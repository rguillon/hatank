# Asynchronous Home Assistant compatible mqtt platform for monitor and control
# of fish tanks
# (C) Copyright Renaud Guillon 2020.
# Released under the MIT licence.



try:
    import asyncio
except ImportError:
    import uasyncio as asyncio

import ha_mqtt

import ha_mqtt_light
import ha_mqtt_switch
from drivers import BasicLightDriver, BrightnessLightDriver, RgbLightDriver, SwitchDriver


ha_mqtt_light.HaMqttBasicLight(name="light01", light=BasicLightDriver(14))
ha_mqtt_light.HaMqttBrightnessLight(name="light02", light=BrightnessLightDriver(14))
ha_mqtt_light.HaMqttRgbLight(name="light04", light=RgbLightDriver(14,15,16))
ha_mqtt_switch.HaMqttSwitch(name="switch01", switch=SwitchDriver(14))

try:
    asyncio.get_event_loop().run_forever()
finally:
    ha_mqtt.close_client()  # Prevent LmacRxBlk:1 errors
