import threading
import time
import requests
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
 
import socket
import sys

# Prevent multiple instances using socket lock
def single_instance(port=65432):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("localhost", port))
    except socket.error:
        print("Another instance is already running.")
        sys.exit()
    return s  # keep socket open to maintain lock

# Call this before anything else
lock_socket = single_instance()



# CONFIGURATION
CHECK_URL = "https://integrity.st/"
TARGET_STRING = "Du ansluter via"
CHECK_INTERVAL = 30  # in seconds

# ICONS
def create_icon(color):
    image = Image.new("RGB", (64, 64), color)
    draw = ImageDraw.Draw(image)
    draw.ellipse((16, 16, 48, 48), fill=(255, 255, 255))
    return image

green_icon = create_icon("green")
red_icon = create_icon("red")

# GLOBALS
icon = None
current_status = None  # to track status and avoid unnecessary icon updates

# CHECK FUNCTION
def check_website():
    global current_status
    while True:
        try:
            response = requests.get(CHECK_URL, timeout=10)
            if TARGET_STRING in response.text:
                if current_status != "green":
                    icon.icon = green_icon
                    icon.title = f"Status: Found '{TARGET_STRING}'"
                    current_status = "green"
            else:
                if current_status != "red":
                    icon.icon = red_icon
                    icon.title = f"Status: Missing '{TARGET_STRING}'"
                    current_status = "red"
        except Exception as e:
            if current_status != "red":
                icon.icon = red_icon
                icon.title = f"Error checking site"
                current_status = "red"
        time.sleep(CHECK_INTERVAL)

# QUIT FUNCTION
def on_quit(icon, item):
    icon.stop()

# MAIN FUNCTION
def setup_tray():
    global icon
    menu = Menu(MenuItem('Quit', on_quit))
    icon = Icon("WebChecker", green_icon, "Checking site...", menu)
    threading.Thread(target=check_website, daemon=True).start()
    icon.run()

if __name__ == "__main__":
    setup_tray()
