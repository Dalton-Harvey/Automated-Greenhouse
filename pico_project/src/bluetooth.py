import asyncio # for asynchronous tasks (multithreading)
import aioble # bluetooth library installed using mip package manager
import bluetooth # basic bluetooth library

class GATTServer:
    def __init__(self, name):
        """
        Register a GATT server (Generic Attribute Profile server) to advertise what this device can do:
        - create a service and characteristics attached to it
        - register the service
        """
        
        # currently just using made up UUIDs so they are meaningless and dont really tell the client anything useful
        uuids = iter(range(0x5678))
        
        self.my_service = aioble.Service(bluetooth.UUID(next(uuids)), name='MyService')
        
        # readable characteristic. clients can also subscribe to it to get notifications
        self.my_characteristic = aioble.Characteristic(self.my_service, bluetooth.UUID(next(uuids)), read=True, notify=True)
        
        # writeable characteristic. turning capture on allows us to get the data as well. otherwise it just tells who wrote to this without saying what they wrote
        self.my_writeable_characteristic = aioble.Characteristic(self.my_service, bluetooth.UUID(next(uuids)), write=True, capture=True)
        
        aioble.register_services(self.my_service)
        
        self.words = ['hello', 'world', '!']
        
        self.timeout_interval_ms = 250 * 1000
        self.name = name
    
    def get_tasks(self):
        return [
            self.write_to_characteristic,
            self.read_from_characteristic,
            self.advertise,
        ]
    
    async def start_tasks(self):
        tasks = [
            asyncio.create_task(task())
            for task in self.get_tasks()
        ]
        
        await asyncio.gather(*tasks)
    
    async def write_to_characteristic(self):
        # broadcast a different string every second
        idx = 0
        while True:
            # write value, turning on send_update to send out a notification as well for any clients who are subscribed
            self.my_characteristic.write(self.words[idx], send_update=True) 
            idx += 1
            idx %= len(self.words)
            await asyncio.sleep_ms(1000) # type: ignore
    
    async def read_from_characteristic(self):
        while True:
            # wait for a write, then report who sent it and what they were sending, then repeat
            connection, data = await self.my_writeable_characteristic.written() # type: ignore
            print(f'{connection.device} says: {data}')
            self.words.append(data)
    
    # advertise and wait for a connection, then wait for a disconnect before going back to advertising
    async def advertise(self):
        while True:
            # you can advertise what services/characteristics you offer if you want, but im not doing that here
            print(f'Advertising as {self.name}...')
            async with await aioble.advertise(self.timeout_interval_ms, name=self.name) as connection: # type: ignore
                print(f'Connected to {connection.device}')
                await connection.disconnected()
                print(f'Disconnected from {connection.device}')


gatt_server = GATTServer('ROSS_PICO_0')
asyncio.run(gatt_server.start_tasks())