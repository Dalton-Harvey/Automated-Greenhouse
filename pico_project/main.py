import rp2
from machine import Pin
import asyncio
from src import soil_sensor

button_up_event = asyncio.Event()
button_down_event = asyncio.Event()

pump_pin = Pin(16, Pin.OUT)
pump_pin.off()
pump_lock = asyncio.Lock()


async def activate_pump(s):
    """Run pump for {s} seconds"""
    
    async with pump_lock:
        print(f'Pump activating for {s} seconds. Acquired lock')
        pump_pin.on()
        await asyncio.sleep(s)
        pump_pin.off()
        print(f'Pump off. Releasing lock')


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


async def pump_on_button_up():
    while True:
        await button_up_event.wait()
        print('Button pressed')
        await activate_pump(5)


async def collect_moisture_readings():
    sliding_window_size = 3
    sliding_window = []
    sample_delay = 5
    threshold = 350
    
    sensor = soil_sensor.SoilSensor()
    
    while True:
        reading = sensor.moisture()
        sliding_window.append(reading)
        
        while len(sliding_window) > sliding_window_size:
            sliding_window.pop(0)
        
        print(f'Avg: {sum(sliding_window) / len(sliding_window):.0f} - Size: {len(sliding_window)}/{sliding_window_size} - Sliding Window: {sliding_window}')
        
        if len(sliding_window) == sliding_window_size and sum(sliding_window) / len(sliding_window) < threshold:
            await activate_pump(5)
            sliding_window = []
        
        await asyncio.sleep(sample_delay)


async def main():
    await asyncio.gather(
        button_listener(),
        pump_on_button_up(),
        collect_moisture_readings()
    )


asyncio.run(main())