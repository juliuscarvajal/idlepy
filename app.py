import ctypes
from ctypes import Structure, windll, c_uint, sizeof, byref
import win32con
import win32process
import win32gui
import subprocess

# constants
PLAYER_CLASS_NAME = 'Chrome_WidgetWin_1'
SHOW_WIN = win32con.SW_MAXIMIZE
HIDE_WIN = win32con.SW_MINIMIZE
BROWSER_PATH = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
URL = 'https://mcdonalds.com.au/'

# Shortcuts to win32 apis
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
GetClassName = ctypes.windll.user32.GetClassNameW
ShowWindow = ctypes.windll.user32.ShowWindow

player_hwnd = None

class LASTINPUTINFO(Structure):
  _fields_ = [
    ('cbSize', c_uint),
    ('dwTime', c_uint),
  ]

  def get_idle_duration():
    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = sizeof(lastInputInfo)
    windll.user32.GetLastInputInfo(byref(lastInputInfo))
    millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
    return millis / 1000.0

  def run_player():
    return subprocess.Popen([BROWSER_PATH,  '--kiosk', '--disable-session-crashed-bubble', '--disable-infobars', URL])

  def get_player_window():
    def foreach_window(hwnd, lParam):
      if IsWindowVisible(hwnd):
        length = GetWindowTextLength(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetClassName(hwnd, buff, length + 1)

        if buff.value == PLAYER_CLASS_NAME:
          global player_hwnd
          player_hwnd = hwnd

          return True

        EnumWindows(EnumWindowsProc(foreach_window), 0)

        while True:
          print "Player has run..."
          player = run_player()
          print player
          while player.poll is not None:
            if player_hwnd is None:
              get_player_window()
              else:
                idle = get_idle_duration()
                if idle > 5:
                  ShowWindow(player_hwnd, SHOW_WIN)
                  else:
                    ShowWindow(player_hwnd, HIDE_WIN)

                    print "Player has died..."
                    player_hwnd = None

