import asyncio
import websockets
import pyautogui
import keyboard
import yaml

pause_script = False

async def check_for_pause():
    global pause_script
    while True:  # Continuously check for the pause key
        if keyboard.is_pressed('ctrl+shift+space'):  # Check if the pause key combination is pressed
            pause_script = not pause_script  # Toggle the pause state
            print("Pausing..." if pause_script else "Resuming...")
            while keyboard.is_pressed('ctrl+shift+space'):  # Wait for the key combination to be released
                await asyncio.sleep(0.1)  # Non-blocking wait
            if pause_script:
                print("Paused. Press 'ctrl+shift+space' to resume.")
            else:
                print("Resumed.")
        await asyncio.sleep(0.1)  # Check every 0.1 seconds to reduce CPU usage

async def message_handler(uri):
    async with websockets.connect(uri) as websocket:
        async for message in websocket:
            if pause_script:
                await asyncio.sleep(1)  # Wait a bit before checking again if the script is still paused
                continue
            print(f"Message received: {message}")
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