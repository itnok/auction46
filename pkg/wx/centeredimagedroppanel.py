#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import wx
import platform
import darkdetect


class CenteredImageDropPanel(wx.Panel):
    def __init__(self, parent, image_file):
        super().__init__(parent)

        img = wx.StaticBitmap(self, id=wx.ID_ANY,
                              bitmap=wx.Image(image_file).Scale(128, 128).ConvertToBitmap())
        txt = wx.StaticText(self, id=wx.ID_ANY,
                            label="\nDrop here PDF files you want to process...",
                            style=wx.ALIGN_CENTRE_HORIZONTAL)
        txt.SetForegroundColour((96, 96, 96))
        txt.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT,
                            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        v_sizer = wx.BoxSizer(wx.VERTICAL)
        v_sizer.AddStretchSpacer()
        v_sizer.Add(img, proportion=0,
                    flag=wx.CENTER, border=0)
        v_sizer.Add(txt, proportion=0,
                    flag=wx.CENTER, border=0)
        v_sizer.AddStretchSpacer()
        if platform.system() == "Darwin" and darkdetect.isDark():
            self.SetBackgroundColour(
                wx.Colour(32, 32, 32, alpha=wx.ALPHA_OPAQUE))
        else:
            self.SetBackgroundColour(
                wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        self.SetSizer(v_sizer)


if __name__ == "__main__":
    import sys
    print(
        f"{sys.argv[0]} is a module and it is NOT supposed to be called directly!")
