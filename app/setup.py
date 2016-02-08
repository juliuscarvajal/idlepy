from distutils.core import setup
import py2exe, sys
import os

app_name = 'app.exe'

os.system('taskkill /f /im ' + app_name)

sys.argv.append('py2exe')

setup(
  name='Switcheroo',
  version='0.1',
  description='A background app that switches to the player when the kiosk is idle and restores the kiosk app once the kiosk gains user interaction.',
  author='Julius Carvajal',
  author_email='juliuscarvajal21@gmail.com',
  options = {'py2exe' : {'optimize' : 2}},
  windows = [{'script' : 'app.py'}],
  data_files = [('', ['config.ini.prod', 'forever.bat'])],
  zipfile = None,
)

os.rename('./dist/config.ini.prod', './dist/config.ini')
