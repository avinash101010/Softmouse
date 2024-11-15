# Softmouse

Softmouse enables you to use your mobile device as a remote control for your computer's mouse. The application supports essential mouse actions like moving the cursor, clicking, and scrolling, and includes an authentication feature for secure access.

## Features

- **Move Mouse**: Use the mobile device's touchpad area to control the computer's cursor.
- **Left & Right Click**: Dedicated buttons for performing left and right mouse clicks.
- **Scroll Up & Down**: Scroll functionality using up and down buttons.
- **Authentication**: Each session requires a unique token generated by the server for secure client connections.

## Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/avinash101010/Softmouse.git
   cd softmouse
   ```
2. **Create a Virtual Environment (recommended)**:
   ```bash
   python -m venv myenv
   ```
3. **Install Required Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Running Softmouse

1. **Start server**:
    ```bash
    python server.py
    ```
    or
    ```bash
    python3 server.py
    ```
    The server will display the computer's IP address and a unique token in the terminal. Note these, as they are required for client access.
2. **Using Client**:
- Open the client.html file on your mobile device’s browser.
- Enter the IP address and token generated by the server.
- Press Connect to establish the connection.

3. **Control Your Computer’s Mouse**:
- Move the cursor by dragging within the touchpad area.
- Use the Left Click and Right Click buttons for mouse clicks.
- Use the UP and DOWN buttons to scroll.

4. **Disconnecting**:

- Press the Disconnect button on your mobile to safely end the session.
- If you want to reconnect, restart the server to get a new token.

## Notes
Ensure both your computer and mobile device are connected to the same network for smooth communication. 