# Requisites:
- Windows machine
- Install py2exe: http://www.py2exe.org/
- Install pywinauto: http://pywinauto.github.io/
- Install wixEdit: http://wixedit.sourceforge.net/


# To create an installer:
- Download latest Wix http://wixtoolset.org/releases/
- Download googlechromestandaloneenterprise.msi
- In command line: 
```   
candle setup.wxs
light setup.wixobj
   
candle bundle.wxs -ext WixBalExtension
light bundle.wixobj -ext WixBalExtension
```

- Distribute bundle.exe
- Run bundle.exe as admin


# Editing installers
- Use Wix Edit for setup.wxs
- Use any text editor for bundle.wxs
