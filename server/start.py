import asyncio
import websockets
import time
import busio
import board
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

connected = set()  # Set of connected WebSocket clients

async def count_heartbeats(chan):
    last_beat_time = 0
    beat_count = 0
    readings = []  # Store recent voltage readings
    moving_avg_window = 10  # Number of readings to calculate moving average

    # Initial loop to gather the first 10 voltage readings
    while len(readings) < moving_avg_window:
        voltage = chan.voltage
        if voltage < 2:
            await asyncio.sleep(0.2)
            continue
        readings.append(voltage)
        print("Syncing...")
        await asyncio.sleep(0.5)

    try:
        print("Sync completed")
        while True:
            voltage = chan.voltage
            readings.append(voltage)
            if len(readings) > moving_avg_window:
                readings.pop(0)  # Remove the oldest reading

            moving_avg = sum(readings) / len(readings)
            dynamic_threshold = moving_avg * 1.618  # Adjust multiplier as needed

            if voltage > dynamic_threshold and (time.time() - last_beat_time) > 0.5:
                beat_count += 1
                last_beat_time = time.time()
                print(f"Heartbeat detected! Total count: {beat_count}")
                message = f"Heartbeat detected! Total count: {beat_count}"
                await asyncio.gather(*(client.send(message) for client in connected))
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        print(f"Final heartbeat count: {beat_count}")

async def server(websocket, path):
    connected.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        connected.remove(websocket)


if __name__ == '__main__':
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1015(i2c)
    ads.gain = 2/3
    chan = AnalogIn(ads, ADS.P0)

    start_server = websockets.serve(server, "0.0.0.0", 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().create_task(count_heartbeats(chan))
    asyncio.get_event_loop().run_forever()
