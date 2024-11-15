import sys
import pyautogui
import asyncio
import websockets
import secrets
import time
import socket
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QHBoxLayout
)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QClipboard


# Global server state
is_running = True
movement_accumulator = [0, 0]
last_move_time = time.time()
AUTH_TOKEN = secrets.token_hex(16)

# Get LAN IP address
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
IPAddr = s.getsockname()[0]
s.close()

# WebSocket Handler
async def handler(websocket, path):
    global is_running, movement_accumulator, last_move_time
    async for message in websocket:
        parts = message.split()

        if parts[0] != AUTH_TOKEN:
            print("Unauthorized access attempt.")
            continue

        command, *args = parts[1:]
        try:
            if command == "MOVET":
                x, y = map(int, args)
                pyautogui.moveTo(x, y)
            elif command == "MOVE":
                dx, dy = map(int, args)
                movement_accumulator[0] += int(dx)
                movement_accumulator[1] += int(dy)
                movement_speed = (dx**2 + dy**2)**0.5
                delay = max(0.005, min(0.02, 0.02 - (movement_speed / 100)))
                if time.time() - last_move_time > delay:
                    pyautogui.moveRel(*movement_accumulator)
                    movement_accumulator = [0, 0]
                    last_move_time = time.time()
            elif command == "CLICK":
                pyautogui.click()
            elif command == "RIGHT_CLICK":
                pyautogui.rightClick()
            elif command == "SCROLL":
                direction = args[0].upper()
                if direction == "UP":
                    pyautogui.scroll(5)
                elif direction == "DOWN":
                    pyautogui.scroll(-5)
            elif command == "WIN":
                pyautogui.hotkey('win')
            elif command == "TAB":
                pyautogui.hotkey('tab')
            elif command == "ENTER":
                pyautogui.press('enter')
            elif command == "DISCONNECT":
                await websocket.close()
                is_running = False
                break
        except Exception as e:
            print(f"Error processing command: {e}")

# WebSocket Server
class WebSocketServer(QThread):
    update_log = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.server = None

    async def start_server(self):
        global is_running
        try:
            self.server = await websockets.serve(handler, "0.0.0.0", 12345)
            self.update_log.emit("Server is running...")
            await asyncio.Future()  # Run forever
        except asyncio.CancelledError:
            self.update_log.emit("Server shutting down...")
        finally:
            if self.server is not None:
                self.server.close()
                await self.server.wait_closed()
                self.update_log.emit("Server stopped.")

    def run(self):
        try:
            asyncio.run(self.start_server())
        except KeyboardInterrupt:
            self.update_log.emit("Server manually stopped")

    def stop_server(self):
        global is_running
        is_running = False

# PyQt5 Desktop Application
class ServerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.server_thread = None

    def initUI(self):
        self.setWindowTitle('WebSocket Server')
        self.layout = QVBoxLayout()

        # Display server information
        self.ip_label = QLabel(f'IP Address: {IPAddr}', self)
        self.token_label = QLabel(f'Token: {AUTH_TOKEN}', self)

        # Add copy button for the token
        token_layout = QHBoxLayout()
        token_layout.addWidget(self.token_label)
        copy_button = QPushButton('Copy')
        copy_button.clicked.connect(self.copy_token)
        token_layout.addWidget(copy_button)
        self.layout.addLayout(token_layout)

        # Display status
        self.status_label = QLabel('Status: Waiting for connection...', self)
        self.layout.addWidget(self.ip_label)
        self.layout.addWidget(self.status_label)

        # Log text area
        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)
        self.layout.addWidget(self.log_text)

        # Start button
        self.start_button = QPushButton('Start Server', self)
        self.start_button.clicked.connect(self.start_server)
        self.layout.addWidget(self.start_button)

        # Stop and close button
        self.stop_button = QPushButton('Stop Server and Close', self)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_and_close)
        self.layout.addWidget(self.stop_button)

        self.setLayout(self.layout)
        self.setStyleSheet(self.get_dark_theme_stylesheet())
        self.show()

    def start_server(self):
        global is_running
        is_running = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.server_thread = WebSocketServer()
        self.server_thread.update_log.connect(self.update_log)
        self.server_thread.start()

    def stop_and_close(self):
        global is_running
        is_running = False
        if self.server_thread and self.server_thread.isRunning():
            self.server_thread.terminate()
            self.server_thread.wait()
            self.server_thread = None
        self.update_log("Server stopped.")
        QApplication.quit()

    def update_log(self, message):
        self.log_text.append(message)
        self.status_label.setText(f'Status: {message}')

    def copy_token(self):
        """Copy the token to the clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(AUTH_TOKEN)
        self.log_text.append("Token copied to clipboard!")

    def closeEvent(self, event):
        """Handle window close event to stop the server safely."""
        print('Closing Application...')
        
        if self.server_thread and self.server_thread.isRunning():
            self.server_thread.terminate()
            self.server_thread.wait()
        event.accept()

    @staticmethod
    def get_dark_theme_stylesheet():
        """Return a stylesheet for dark theme.""" 
        #here """ is used to write multi line string but to comment multiple lines we use ''' ''' 
        return """ 
        QWidget {
            background-color: #2E2E2E;
            color: #F1F1F1;
        }
        QPushButton {
            background-color: #444;
            color: #F1F1F1;
            border: 1px solid #555;
            border-radius: 5px;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #555;
        }
        QPushButton:pressed {
            background-color: #666;
        }
        QTextEdit, QLabel {
            background-color: #3E3E3E;
            border: 1px solid #555;
            padding: 5px;
        }
        """

# Main Application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ServerApp()
    sys.exit(app.exec_())
