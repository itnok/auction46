#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import wx
import math
import platform
import darkdetect

from pubsub import pub
from typing import List


class ProgressDlg(wx.Dialog):
    def __init__(self, queue=List[str]):
        super().__init__(
            None, title="Data extraction...", size=(500, 100))
        self._q = queue.copy()
        self._now = 0
        self.progress = wx.Gauge(self, range=len(self._q) * 2, size=(350, -1))
        self.percent = wx.StaticText(self, id=wx.ID_ANY,
                                     label="0%",
                                     style=wx.ALIGN_RIGHT)
        self.percent.SetForegroundColour((96, 96, 96))
        self.percent.SetFont(
            wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddStretchSpacer()
        sizer.Add(self.progress, 0, wx.EXPAND)
        sizer.AddStretchSpacer()
        sizer.Add(self.percent, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        sizer.AddStretchSpacer()
        if platform.system() == "Darwin" and darkdetect.isDark():
            self.SetBackgroundColour(
                wx.Colour(32, 32, 32, alpha=wx.ALPHA_OPAQUE))
        else:
            self.SetBackgroundColour(
                wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        self.SetSizer(sizer)

        pub.subscribe(self.onProgress, "update")

    def onProgress(self, msg):
        self._now += 1
        if self._now >= 2 * len(self._q):
            self.EndModal(wx.ID_OK)
        self.progress.SetValue(self._now)
        self.percent.SetLabel(
            f"{math.ceil(self._now / (2 * len(self._q)) * 100)}%")


if __name__ == "__main__":
    import sys
    print(
        f"{sys.argv[0]} is a module and it is NOT supposed to be called directly!")
