# Requisites:
- Windows machine

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



