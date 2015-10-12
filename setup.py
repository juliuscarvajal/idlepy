from distutils.core import setup
import py2exe, sys
import os

sys.argv.append('py2exe')

app_name = 'app.exe'
os.system('taskkill /f /im ' + app_name)

setup(
  options = {'py2exe' : { 'optimize' : 2}},
  windows = [{'script' : "app.py"}],
  zipfile = None,
)

'''
setup(
  name = 'coates-screen-saver',
  version = '1.0',
  scripts = ['app.py', 'idle.py'],
  description = 'Coates Digital Screen Saver Application',
  author = 'Coates Digital'
)
'''
