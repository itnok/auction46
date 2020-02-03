#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This is a collection of useful details about the app
"""

_INFO = {
    "name": "Auction46",
    "version": "1.0.0",
    "bundle": "com.itnok.",
    "copyright": "© 2020 Simone Conti. All Rights Reserved.",
}


class About:
    @staticmethod
    def GetAppName() -> str:
        return _INFO["name"]

    @staticmethod
    def GetAppVersion() -> str:
        return _INFO["version"]

    @staticmethod
    def GetAppBundleStr() -> str:
        return f"{_INFO['bundle']}{_INFO['name'].lower()}"

    @staticmethod
    def GetAppCopyright() -> str:
        return f"{_INFO['copyright']}"
