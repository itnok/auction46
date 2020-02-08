#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import wx
import wx.adv

from pubsub import pub
from typing import List
from app_info import About
from pkg.workerthread import WorkerThread
from pkg.wx.progressdlg import ProgressDlg
from pkg.wx.pdfdroptarget import PDFDropTarget
from pkg.wx.centeredimagedroppanel import CenteredImageDropPanel


class Auction46Frame(wx.Frame):
    def __init__(self):
        super().__init__(
            parent=None, title=wx.GetApp().GetAppName(), size=wx.Size(512, 512))
        self._pdf_list: List[str] = list()
        self._resources_dir: str = wx.StandardPaths.Get().GetResourcesDir()
        self.InitUI()
        pub.subscribe(self.doExtractData, "work")

    def InitUI(self):
        self.SetMinSize(size=wx.Size(512, 512))

        self.menubar = wx.MenuBar()

        menu_file = wx.Menu()
        item = menu_file.Append(id=wx.ID_EXIT, item="&Quit\tCtrl+Q")
        self.Bind(wx.EVT_MENU, self.OnQuit, item)
        item = menu_file.Append(id=wx.ID_OPEN, item="&Open\tCtrl+O")
        self.Bind(wx.EVT_MENU, self.OnOpen, item)
        self.menubar.Append(menu_file, "&File")

        menu_help = wx.Menu()

        # this gets put in the App menu on macOS
        item = menu_help.Append(wx.ID_ABOUT, f"&About {About.GetAppName()}",
                                f"More information About {About.GetAppName()}")
        self.Bind(wx.EVT_MENU, self.OnAbout, item)
        self.menubar.Append(menu_help, "&Help")

        self.SetMenuBar(self.menubar)

        self.panel = CenteredImageDropPanel(self, os.path.join(
            self._resources_dir, "pdf-drop-target.png"))
        self.pdf_drop_target = PDFDropTarget()
        self.panel.SetDropTarget(self.pdf_drop_target)

    def OnOpen(self, event):
        with wx.FileDialog(self, message="Open PDF file", wildcard="PDF files (*.pdf)|*.pdf",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE) as dlg_open_file:
            if dlg_open_file.ShowModal() == wx.ID_CANCEL:
                return
            self.doExtractData(filenames=dlg_open_file.GetPaths())

    def OnQuit(self, event):
        self.Close()
        wx.GetApp().ExitMainLoop()

    def OnAbout(self, event):
        info = wx.adv.AboutDialogInfo()
        info.Name = About.GetAppName()
        info.Version = About.GetAppVersion()
        info.Copyright = About.GetAppCopyright()
        wx.adv.AboutBox(info)

    def doExtractData(self, filenames: List[str] = list()):
        if filenames:
            self._pdf_list += filenames
        WorkerThread(self._pdf_list)
        dlg = ProgressDlg(self._pdf_list)
        dlg.ShowModal()
        self._pdf_list = list()


if __name__ == "__main__":
    import sys
    print(
        f"{sys.argv[0]} is a module and it is NOT supposed to be called directly!")
