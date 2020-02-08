#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import wx
import time

from pubsub import pub
from typing import List
from threading import Thread
from pkg.auction46pdf import Auction46PDF


class WorkerThread(Thread):
    def __init__(self, queue: List[str]):
        super().__init__()
        self._q = queue.copy()
        self.start()

    def run(self):
        for idx, val in enumerate(self._q):
            p = Auction46PDF(val)
            t = p.get_txt_from_page(p._pages - 1)
            wx.CallAfter(pub.sendMessage, "update", msg=val)
            wx.GetApp().Yield()
            time.sleep(0.5)
            bidder = p.get_bidders_from_txt(key="is as follows:", txt=t)
            bidder.sort()
            p.save_bidders_to_csv(bidder)
            wx.CallAfter(pub.sendMessage, "update", msg=val)
            wx.GetApp().Yield()


if __name__ == "__main__":
    import sys
    print(
        f"{sys.argv[0]} is a module and it is NOT supposed to be called directly!")
