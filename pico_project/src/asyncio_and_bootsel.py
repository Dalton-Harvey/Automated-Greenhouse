import rp2
from machine import Pin
import asyncio
import time


button_up_event = asyncio.Event()
button_down_event = asyncio.Event()


async def button_listener():
    previous_state = rp2.bootsel_button()
    
    while True:
        state = rp2.bootsel_button()
        
        # detect button press
        if previous_state == 0 and state == 1:
            button_down_event.set() # awaken all currently waiting tasks
            button_down_event.clear() # immediately clear so future waiting tasks have to wait for the next button press
        
        # detect button release
        if previous_state == 1 and state == 0:
            button_up_event.set() # awaken all currently waiting tasks
            button_up_event.clear() # immediately clear so future waiting tasks have to wait for the next button press
        
        previous_state = state
        
        # await a short time, people cant really manage to click for less than this so this should get all button presses
        await asyncio.sleep(0.025)


async def manage_led():
    led = Pin(16, Pin.OUT)
    while True:
        await button_up_event.wait()
        led.toggle()


async def count():
    i = 0
    while True:
        await button_up_event.wait()
        print(i)
        i += 1


async def fibonacci():
    a, b = 0, 1
    while True:
        await button_up_event.wait()
        print(a)
        b = a + b
        a = b - a


async def main():
    await asyncio.gather(
        button_listener(),
        manage_led(),
        fibonacci(),
        count(),
    )


asyncio.run(main())