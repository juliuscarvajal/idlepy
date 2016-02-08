# This only works on Windows
# TODO: Detect player crash (chrome) and react to it.
import os

log_file = './log/app.log'
log_dir = os.path.dirname(log_file)
try:
  os.stat(log_dir)
except:
  os.mkdir(log_dir)

import logging
logging.basicConfig(filename = log_file, filemode = 'w', level = logging.DEBUG)
Logger = logging.getLogger(__name__)

import pywinauto
from pywinauto import Application, timings, findwindows, win32structures, win32functions
from pywinauto.controls.HwndWrapper import HwndWrapper

import ctypes
from idle import idle_check
from scan import scan_source_player, source_player_alive
import time
import datetime
import threading

import ConfigParser
Config = ConfigParser.ConfigParser()
Config.read('config.ini')

def set_config(section, name, default = None):
  val = None
  try:
    val = Config.get(section, name)
  except:
    val = '' if default is None else default

  return val

# https://msdn.microsoft.com/en-us/library/windows/desktop/ms633548(v=vs.85).aspx
SHOW_WIN = 3
HIDE_WIN = 6

IDLE_TRIGGER = int(set_config('DEFAULT', 'IDLE_TRIGGER', '5'))
KIOSK_FIND_BY = set_config('DEFAULT', 'KIOSK_FIND_BY')
KIOSK_CLASS_NAME = set_config('DEFAULT', 'KIOSK_CLASS_NAME')
KIOSK_WINDOW_NAME = set_config('DEFAULT', 'KIOSK_WINDOW_NAME')
PLAYER_CLASS_NAME = set_config('DEFAULT', 'PLAYER_CLASS_NAME', 'Chrome_WidgetWin_1')
PROCESS_NAME = set_config('DEFAULT', 'PROCESS_NAME', 'chrome.exe')
BROWSER_PATH = set_config('DEFAULT', 'BROWSER_PATH', 'C:/Program Files/Google/Chrome/Application/chrome.exe')
MP_SWITCH_INTERVAL = int(set_config('DEFAULT', 'MP_SWITCH_INTERVAL', '300')) # 5 minutes

# Shortcuts to win32 apis
SetConsoleCtrlHandler = ctypes.windll.kernel32.SetConsoleCtrlHandler
IsHungAppWindow = ctypes.windll.user32.IsHungAppWindow

class Player:
  '''
  def dummy(self):
    windows = findwindows.enum_windows()
    for win in windows:
      w = HwndWrapper(win)
      if w.IsVisible():
        Logger.info('[' + w.Class() + '] -- [' + w.WindowText() + '] -- [' + str(w.ProcessID()) + ']')

    try:
      h = self.get_kiosk()
    except:
      Logger.info("No kiosk running")
  '''

  def __init__(self):
    Logger.info("Switch interval: " + str(MP_SWITCH_INTERVAL))
    self.currentSource = None
    self.player = Application()
    self.kiosk = Application()
    self.visible = False
    self.kill()

  def get_player(self):
    try:
      return findwindows.find_window(class_name = PLAYER_CLASS_NAME)
    except Exception, err:
      raise err

  def get_kiosk(self):
    try:
      if KIOSK_FIND_BY == 'KIOSK_WINDOW_NAME':
        h = findwindows.find_window(title = KIOSK_WINDOW_NAME)
      elif KIOSK_FIND_BY == 'KIOSK_CLASS_NAME':
        h = findwindows.find_window(class_name_re = KIOSK_CLASS_NAME)

      Logger.info('Kiosk hwnd: ' + str(h))
      Logger.info('Kiosk class: ' + HwndWrapper(h).Class())
      Logger.info('Kiosk title: ' + HwndWrapper(h).WindowText())
      return h
    except Exception, err:
      raise err

  def ready(self):
    try:
      timings.WaitUntilPasses(2, 0.5, self.get_player)
    except:
      self.run()
      return False

    return True

  def run(self):
    player = self.currentSource

    if player is not None:
      Logger.info("Running player: " + player + " " + str(datetime.datetime.now()))
      args = '--disable-session-crashed-bubble' + ' ' + '--disable-infobars' + ' ' + '--kiosk'
      self.player.start(BROWSER_PATH + ' ' + args + ' ' + player + '/player') #URL)

  def clickthru(self):
    try:
      kiosk = self.get_kiosk()

      rect = win32structures.RECT()
      win32functions.GetWindowRect(kiosk, ctypes.byref(rect))

      x = rect.right
      y = rect.bottom

      Logger.debug('Setting clickthru at ' + str(x) + ', ' + str(y))
      HwndWrapper(kiosk).ClickInput(coords = (x, y))
    except:
      Logger.info("No kiosk running")

  def hide(self):
    try:
      player = self.get_player()
      HwndWrapper(player).Minimize()
    except:
      Logger.info("No player running")

    if self.visible is True:
      self.clickthru()

    self.visible = False

  def set_source(self, source):
    if self.currentSource != source:
      self.kill()

    self.currentSource = source

  def show(self):
    try:
      player = self.get_player()
      if self.hang(player):
        return
      HwndWrapper(player).Maximize()
      self.visible = True
    except:
      Logger.info("No player running")

  def hang(self, playerHwnd):
    # if the player hangs, restart again. cannot test to see if it works
    if IsHungAppWindow(playerHwnd):
      logging.info("Hang")
      self.kill()
      return True
    return False

  def kill(self):
    os.system('taskkill /f /im ' + PROCESS_NAME)

  def exit_handler(self):
    Logger.info("killed self")
    self.kill()

if __name__ == '__main__':
  player = Player()

  def set_exit_handler(func):
    SetConsoleCtrlHandler(func, 1)

  def exit_handler(dwCtrlType):
    retcode = 0
    if dwCtrlType == 0: # CTRL+C
      player.exit_handler()
      retcode = 1
    return retcode

  exit_handler = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_uint)(exit_handler)
  set_exit_handler(exit_handler)

  def set_interval(func, sec):
    def func_wrapper():
      set_interval(func, sec)
      func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

  def scan():
    player.set_source(next(scanner))

  scanner = scan_source_player()
  player.set_source(next(scanner)) # Run initially as set_interval only executes AFTER the time elapsed.

  t = set_interval(scan, MP_SWITCH_INTERVAL)

  is_idle = idle_check(IDLE_TRIGGER)
  while True:
    if player.ready():
      if next(is_idle):
        player.show()
      else:
        player.hide()

  t.stop();
