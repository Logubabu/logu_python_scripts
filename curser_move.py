import pyautogui
import time

while True:
    # move the cursor 50 pixels to the right
    pyautogui.moveRel(50, 0, duration=0.25)
    # move the cursor back 50 pixels to the left
    pyautogui.moveRel(-50, 0, duration=0.25)
    pyautogui.hotkey('alt', 'tab')
    time.sleep(15)  # wait for 15 seconds before moving the cursor again
