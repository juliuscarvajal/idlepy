@echo off

candle setup.wxs
light setup.wixobj

candle bundle.wxs -ext WixBalExtension
light bundle.wixobj -ext WixBalExtension
