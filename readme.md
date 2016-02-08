# Requisites:
- Windows machine
- Chrome
- Python 2.7
- Install py2exe: http://www.py2exe.org/
- Install netifaces: https://pypi.python.org/pypi/netifaces#downloads
- Install pywinauto: http://pywinauto.github.io/

(Optional)
- Install wixEdit: http://wixedit.sourceforge.net/

# Build steps:
```
cd installer
python setup.py
```

# Creating an installer:
- Download latest Wix http://wixtoolset.org/releases/
- Download googlechromestandaloneenterprise.msi
- Run installer.bat
- Distribute bundle.exe
- In the client machine, Run bundle.exe as admin


# Editing installers:
- Use WixEdit for setup.wxs
- Use any text editor for bundle.wxs (WixEdit does not support Bundles)

# Configuration files:
- config.ini <-- Main configuration settings file.
- defaults.ini <-- Fallback if config.ini does not exist
- overrides.ini <-- If this file exists, the config settings in the overrides.ini will override the corresponding settings in config.ini. Config settings not specified in the overrides.ini will follow the settings in config.ini
