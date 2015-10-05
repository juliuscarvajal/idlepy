from distutils.core import setup
import py2exe, sys

sys.argv.append('py2exe')

setup(
  options = {'py2exe' : { 'optimize' : 1}},
  windows = [{'script' : "app.py"}],
  zipfile = None,
)

