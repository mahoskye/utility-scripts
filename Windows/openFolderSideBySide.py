#################################################
# Open two folders side by side on Windows
#
# It's not 100% reliable, but it works most of the time.
#################################################
import subprocess
import time

# Check if pygetwindow and pyautogui are installed
try:
    import pygetwindow as gw
    import pyautogui
except ImportError as e:
    missing_package = str(e).split()[-1]
    print(f"Missing required package: {missing_package}.")
    print(f"pip install {missing_package}")
    exit(1)

# Define the folder paths
folders = {
    'left': r"C:\Users",
    'right': r"C:\Windows"
}

MAX_ATTEMPTS = 10


def get_title_from_path(path):
    # Windows uses the last folder name as the window title
    return path.split("\\")[-1]


def is_window_open(title):
    # Check if the window is open
    return any(win.title == title for win in gw.getAllWindows())


# Open the folders side by side
for side, path in folders.items():
    title = get_title_from_path(path)

    # When the folder is not open, open it
    if not is_window_open(title):
        subprocess.Popen(['explorer', path])
        open_attempts = 1

        # Wait for the window to open, but not forever
        while not is_window_open(title):
            if open_attempts > MAX_ATTEMPTS:
                break
            open_attempts += 1
            time.sleep(0.5)

    # Activate the window
    else:
        gw.getWindowsWithTitle(title)[0].activate()

    # Move the window to the side
    pyautogui.hotkey('win', side)
