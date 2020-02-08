#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import wx

from pubsub import pub
from typing import List


class PDFDropTarget(wx.FileDropTarget):
    def __init__(self):
        super().__init__()

    def OnDropFiles(self, x: int, y: int, filenames: List[str]) -> bool:
        if filenames:
            wx.CallAfter(pub.sendMessage, "work", filenames=filenames)
        return True


if __name__ == "__main__":
    import sys
    print(
        f"{sys.argv[0]} is a module and it is NOT supposed to be called directly!")
