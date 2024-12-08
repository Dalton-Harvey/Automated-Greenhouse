from microdot import Microdot, send_file
from microdot.websocket import with_websocket
import network
import random
import asyncio

app = Microdot()


class Queue:
    def __init__(self, max_size=-1):
        self.queue = []
        self.lock = asyncio.Lock()
        self.item_added = asyncio.Event()
        self.max_size = max_size
    
    async def put(self, item):
        async with self.lock:
            self.queue.append(item)
            
            # pop oldest item if max size is exceeded
            if self.max_size > 0 and len(self.queue) > self.max_size:
                self.queue.pop(0)
                
            self.item_added.set()
    
    async def get(self):
        item = None
        
        await self.lock.acquire()
        try:
            while len(self.queue) == 0:
                self.lock.release()
                await self.item_added.wait()
                await self.lock.acquire()
            
            item = self.queue.pop(0)
            if len(self.queue) == 0:
                self.item_added.clear()
        finally:
            self.lock.release()
        
        return item

debug_queue = Queue()

@app.route('/')
async def index(request):
    return send_file('index.html')


@app.route('/debug')
@with_websocket
async def echo(request, ws):
    while True:
        data = await debug_queue.get()
        await ws.send(str(data))


def buggy_code():
    data = random.randint(0, 10)
    if data % 2 == 0:
        raise RuntimeError(f'Generated even number {data}')
    return data


async def run_buggy_code():
    while True:
        try:
            data = buggy_code()
            print(f'Successfully generated data: {data}')
        except RuntimeError as e:
            asyncio.create_task(debug_queue.put(e))
        
        await asyncio.sleep(3)


def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    import time
    while not wlan.isconnected():
        time.sleep(0.5)
    
    ip = wlan.ifconfig()[0]
    
    return ip


async def main():
    ip = connect_wifi('NOKIA-31B1', 'MszQ3gT9tA')
    port = 80 # http
    
    print(f'http://{ip}:{port}')
    
    await asyncio.gather(
        app.start_server(debug=True, host=ip, port=port),
        run_buggy_code(),
    )


asyncio.run(main())