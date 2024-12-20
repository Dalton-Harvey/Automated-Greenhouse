import moisture
import daily_email
import asyncio

async def moisture_control(threshold):
    sample_delay = 5
    moisture_avg = moisture.collect_moisture_readings()
    
    if moisture_avg < threshold:
        await moisture.activate_pump(5)

    await asyncio.sleep(sample_delay)



def main():
    pass


if __name__ == "__main__":
    main()