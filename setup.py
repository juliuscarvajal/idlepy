from distutils.core import setup
import py2exe, sys
import os

sys.argv.append('py2exe')

app_name = 'app.exe'
os.system('taskkill /f /im ' + app_name)

setup(
  name='Switcheroo',
  version='0.1',
  description='A background app that switches to the player when the kiosk is idle and restores the kiosk app once the kiosk gains user interaction.',
  author='Julius Carvajal',
  author_email='juliuscarvajal21@gmail.com',
  options = {'py2exe' : {'optimize' : 2}},
  windows = [{'script' : "app.py"}],
  data_files = [('', ['config.ini', 'user.ini', 'forever.bat'])],
  #data_files = [('', ['config.ini', 'forever.bat'])],
  zipfile = None,
)

