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

# To create an installer:
- Download latest Wix http://wixtoolset.org/releases/
- Download googlechromestandaloneenterprise.msi
- Run installer.bat
- Distribute bundle.exe
- In the client machine, Run bundle.exe as admin


# Editing installers
- Use Wix Edit for setup.wxs
- Use any text editor for bundle.wxs
