#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import wx

from pubsub import pub
from typing import List
from pkg.wx.auction46frame import Auction46Frame


class Auction46App(wx.App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #
        # This catches events when the app is asked
        # to activate by some other process
        #
        self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)

    def OnInit(self) -> bool:
        self._frame = Auction46Frame()
        self._frame.Show()
        self.SetTopWindow(self._frame)
        return True

    def BringWindowToFront(self):
        try:  # it's possible for this event to come when the frame is closed
            self.GetTopWindow().Raise()
        except:
            pass

    def OnActivate(self, event):
        # if this is an activate event, rather than something else, like iconize.
        if event.GetActive():
            self.BringWindowToFront()
        event.Skip()

    def MacOpenFiles(self, filenames: List[str] = list()):
        """
            Called for files droped on dock icon, or opened via finders context menu
        """
        if filenames:
            wx.CallAfter(pub.sendMessage, "work", filenames=filenames)

    def MacReopenApp(self):
        """
            Called when the doc icon is clicked, and ???
        """
        self.BringWindowToFront()

    def MacNewFile(self):
        pass

    def MacPrintFile(self, file_path):
        pass


if __name__ == "__main__":
    import sys
    print(
        f"{sys.argv[0]} is a module and it is NOT supposed to be called directly!")
