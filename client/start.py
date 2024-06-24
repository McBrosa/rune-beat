import asyncio
import websockets
import pyautogui
import keyboard
import yaml

pause_script = False

async def check_for_pause():
    global pause_script
    while True:
        if keyboard.is_pressed('ctrl+shift+space'):
            pause_script = not pause_script
            print("Pausing..." if pause_script else "Resuming...")
            while keyboard.is_pressed('ctrl+shift+space'):
                await asyncio.sleep(0.1)
            if pause_script:
                print("Paused. Press 'ctrl+shift+space' to resume.")
            else:
                print("Resumed.")
        await asyncio.sleep(0.1)

async def message_handler(uri):
    async with websockets.connect(uri) as websocket:
        async for message in websocket:
            if pause_script:
                await asyncio.sleep(1)
                continue
            print(f"Received: {message}")
            pyautogui.click()

async def main():
    with open('config.yml', 'r') as config_file:
        config = yaml.safe_load(config_file)
        server_config = config['Server']
        uri = f"ws://{server_config['address']}:{server_config['port']}"

    task1 = asyncio.create_task(check_for_pause())
    task2 = asyncio.create_task(message_handler(uri))
    await asyncio.gather(task1, task2)

# Run the WebSocket client and pause check concurrently
asyncio.run(main())