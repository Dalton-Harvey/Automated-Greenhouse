from machine import Pin, PWM
from time import sleep

motor = Pin(16, Pin.OUT)
led = Pin('LED', Pin.OUT)

motor.off()
led.off()

while True:
    motor.toggle()
    led.toggle()
    sleep(3)