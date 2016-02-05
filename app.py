# This only works on Windows
# TODO: Detect player crash (chrome) and react to it.

import logging
logging.basicConfig(filename = './app.log', filemode = 'w', level = logging.DEBUG)
Logger = logging.getLogger(__name__)

import pywinauto
from pywinauto import Application, timings, findwindows, win32structures, win32functions
from pywinauto.controls.HwndWrapper import HwndWrapper

import ctypes
import os
from idle import idle_check
from scan import scan_source_player, source_player_alive
import time

import ConfigParser
Config = ConfigParser.ConfigParser()
Config.read('config.ini')

User = ConfigParser.ConfigParser()
User.read('user.ini')

# constants
# https://msdn.microsoft.com/en-us/library/windows/desktop/ms633548(v=vs.85).aspx
try:
  IDLE_TRIGGER = int(User.get('DEFAULT', 'IDLE_TRIGGER'))
  PLAYER_CLASS_NAME = Config.get('DEFAULT', 'PLAYER_CLASS_NAME')
  SHOW_WIN = 3
  HIDE_WIN = 6
  KIOSK_FIND_BY = Config.get('DEFAULT', 'KIOSK_FIND_BY')
  KIOSK_CLASS_NAME = Config.get('DEFAULT', 'KIOSK_CLASS_NAME')
  KIOSK_WINDOW_NAME = Config.get('DEFAULT', 'KIOSK_WINDOW_NAME')
  DELAY_BEFORE_SHOW = float(User.get('DEFAULT', 'DELAY_BEFORE_SHOW'))
  DELAY_BEFORE_HIDE = float(User.get('DEFAULT', 'DELAY_BEFORE_HIDE'))
  PROCESS_NAME = Config.get('DEFAULT', 'PROCESS_NAME')
  BROWSER_PATH = Config.get('DEFAULT', 'BROWSER_PATH')
  URL = User.get('DEFAULT', 'URL')
  MP_HQ = int(Config.get('DEFAULT', 'MP_HQ'))
  MP_RANGE_MIN = int(Config.get('DEFAULT', 'MP_RANGE_MIN'))
  MP_RANGE_MAX = int(Config.get('DEFAULT', 'MP_RANGE_MAX'))
except:
  IDLE_TRIGGER = 5
  PLAYER_CLASS_NAME = 'Chrome_WidgetWin_1'
  SHOW_WIN = 3
  HIDE_WIN = 6
  KIOSK_FIND_BY = ''
  KIOSK_CLASS_NAME = ''
  KIOSK_WINDOW_NAME = ''
  DELAY_BEFORE_SHOW = 0
  DELAY_BEFORE_HIDE = 0
  PROCESS_NAME = 'chrome.exe'
  BROWSER_PATH = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
  URL = ''
  MP_HQ = 100
  MP_RANGE_MIN = 225
  MP_RANGE_MAX = 254

# Shortcuts to win32 apis
SetConsoleCtrlHandler = ctypes.windll.kernel32.SetConsoleCtrlHandler
IsHungAppWindow = ctypes.windll.user32.IsHungAppWindow

class Player:
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

  def __init__(self):
    Logger.info("DELAYS H/S " + str(DELAY_BEFORE_HIDE) + ' ' + str(DELAY_BEFORE_SHOW))
    self.sourcePlayer = scan_source_player()
    self.currentSource = next(self.sourcePlayer)
    self.player = Application()
    self.kiosk = Application()
    self.visible = False
    self.kill()
    #self.dummy()

  def get_player(self):
    if source_player_alive(self.currentSource) is False:
      print("current player is dead... find another...")
      self.kill()
      self.currentSource = next(self.sourcePlayer)

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
      Logger.info("Running player")
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
      if DELAY_BEFORE_HIDE > 0.0:
        time.sleep(DELAY_BEFORE_HIDE)

    self.visible = False

  def show(self):
    if self.visible is False and DELAY_BEFORE_SHOW > 0.0:
      time.sleep(DELAY_BEFORE_SHOW)

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

  is_idle = idle_check(IDLE_TRIGGER)

  while True:
    if player.ready():
      if next(is_idle):
        player.show()
      else:
        player.hide()
