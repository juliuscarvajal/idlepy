Requisites:
1. Windows machine

To create an installer:
1. Download latest Wix http://wixtoolset.org/releases/
2. Download googlechromestandaloneenterprise.msi
3. In command line: 
   ```   
   candle setup.wxs
   light setup.wixobj
   
   candle bundle.wxs -ext WixBalExtension
   light bundle.wixobj -ext WixBalExtension
   ```



