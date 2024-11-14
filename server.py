import pyautogui
import asyncio
import websockets
import time
import secrets
import socket


is_running = True
movement_accumulator = [0, 0]
last_move_time = time.time()
# Generate a secure random token on server startup
AUTH_TOKEN = secrets.token_hex(16)  # Generates a 32-character hexadecimal token
print(f"Server token: {AUTH_TOKEN}")

# This connects to an external address to retrieve the LAN IP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))  # This does not send data, it just determines the LAN IP
IPAddr = s.getsockname()[0]
s.close()

print("Your Computer LAN IP Address is:", IPAddr)

async def handler(websocket, path):#here path is the path of the server for example ws://
    global movement_accumulator, last_move_time
    global is_running
    print("Waiting for connection...")
    async for message in websocket:
        parts = message.split()
        
        # Verify token
        if parts[0] != AUTH_TOKEN:
            print("Unauthorized access attempt.")
            continue
        
        command, *args = parts[1:]
        
        try:
            if command == "MOVET":
                x, y = map(int, args)
                pyautogui.moveTo(x, y)
                print(f"Moved to ({x}, {y})")

            # elif command == "MOVE":
            #     dx, dy = map(float, args)
            #     pyautogui.move(int(dx), int(dy))  # Relative movement
            #     print(f"Moved by ({int(dx)}, {int(dy)})")
            elif command == "MOVE":
                dx, dy = map(int, args)
                movement_accumulator[0] += int(dx)
                movement_accumulator[1] += int(dy)

                movement_speed = (dx**2 + dy**2)**0.5
                delay = max(0.005, min(0.02, 0.02 - (movement_speed / 100)))  # 5-20ms based on speed

                # Only move if enough time has passed
                if time.time() - last_move_time > delay:  # 10ms(delay=0.01)
                    pyautogui.moveRel(*movement_accumulator)
                    movement_accumulator = [0, 0]  # Reset accumulator
                    last_move_time = time.time()

            elif command == "CLICK":
                pyautogui.click()
                print("Clicked")

            elif command == "RIGHT_CLICK":
                pyautogui.rightClick()
                print("Right clicked")

            elif command == "SCROLL":
                # Scroll up or down
                direction = args[0].upper()
                if direction == "UP":
                    pyautogui.scroll(10)
                    print("Scrolled up")
                elif direction == "DOWN":
                    pyautogui.scroll(-10)
                    print("Scrolled down")
            elif command == "DISCONNECT":
                await websocket.close()#this will close the connection

                print("Client disconnected")
                #it should stop the entire server 
                is_running = False       # Stop the server
                break
                

        except Exception as e:
            print(f"Error processing command: {e}")
            pyautogui.moveTo(500,500)

# Set up WebSocket server
async def main():
    global is_running
    async with websockets.serve(handler, "0.0.0.0", 12345):
        print("Server is running...")
        # await asyncio.Future()  # Run forever
        while is_running:
            await asyncio.sleep(1)  # Short sleep to allow other tasks to run

        print("Shutting down server...")

# Run the WebSocket server
# asyncio.run(main())
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Server manually stopped")
