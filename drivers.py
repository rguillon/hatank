# Home Assistant mqtt integration
# (C) Copyright Renaud Guillon 202.
# Released under the MIT licence.

from machine import Pin, PWM


class BasicLightDriver:
    def __init__(self, pin_num):
        self.pin = Pin(pin_num, Pin.OUT)

    def on(self):
        self.pin.on()

    def off(self):
        self.pin.off()

# The LED driver have a common VCC, the polarity needs to be switched

class BasicLightDriver:
    def __init__(self, pin_num):
        self.pin = Pin(pin_num, Pin.OUT)

    def on(self):
        self.pin.off()

    def off(self):
        self.pin.on()


class BrightnessLightDriver:
    def __init__(self, pin_num):
        self.pwm = PWM(Pin(pin_num))

    def brightness(self, value):
        self.pwm.duty(int(1023 * (1.0 - value / 255.0)))

    def on(self):
        self.pwm.duty(0)

    def off(self):
        self.pwm.duty(1023)


class RgbLightDriver:
    def __init__(self, r_pin_num, g_pin_num, b_pin_num):
        self.r_pwm = PWM(Pin(r_pin_num))
        self.g_pwm = PWM(Pin(g_pin_num))
        self.b_pwm = PWM(Pin(b_pin_num))

        self.b = 0
        self.c = {'r': 0, 'g': 0, 'b': 0}

    def on(self):
        self.__update()

    def off(self):
        self.r_pwm.duty(1023)
        self.g_pwm.duty(1023)
        self.b_pwm.duty(1023)

    def color(self, value):
        self.c = value
        self.__update()

    def brightness(self, value):
        self.b = value
        self.__update()

    def __update(self):
        self.r_pwm.duty(int(1023 * (1.0 - self.b * self.c['r'] / 255.0 / 255.0)))
        self.g_pwm.duty(int(1023 * (1.0 - self.b * self.c['g'] / 255.0 / 255.0)))
        self.b_pwm.duty(int(1023 * (1.0 - self.b * self.c['b'] / 255.0 / 255.0)))
