#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import wx
import sys
import csv
import time
import math
import wx.adv
import PyPDF4
import platform
import darkdetect

from typing import List
from threading import Thread
from pubsub import pub
from app_info import About


class PDFdoc:
    _debug: bool = False
    _fname: str = ""
    _pdf: PyPDF4.PdfFileReader
    _info: PyPDF4.pdf.DocumentInformation
    _pages: int = -1

    def __init__(self, pdf_filename: str, debug: bool = False):
        self._debug = debug
        self._fname = pdf_filename
        self._get_doc_information()

    def _get_doc_information(self):
        with open(self._fname, "rb") as f:
            self._pdf = PyPDF4.PdfFileReader(f)
            self._info = self._pdf.getDocumentInfo()
            self._pages = self._pdf.getNumPages()

        if self._debug:
            txt = f"""
            Information about {self._fname}:

            Author: {self._info.author}
            Creator: {self._info.creator}
            Producer: {self._info.producer}
            Subject: {self._info.subject}
            Title: {self._info.title}
            Number of pages: {self._pages}
            """
            print(txt)

    def get_txt_from_page(self, page: int) -> str:
        txt = ""
        with open(self._fname, "rb") as f:
            self._pdf = PyPDF4.PdfFileReader(f)
            p = self._pdf.getPage(page)
            txt = p.extractText()
        return txt


class Auction46(PDFdoc):
    def get_bidders_from_txt(self, key: str, txt: str) -> List[str]:
        lines = txt.splitlines()
        found = False
        result = list()
        for l in lines:
            data = l.strip()
            if found and len(data) > 0:
                result.append(data)
            else:
                haystack = data.lower()
                needle = key.lower().strip()
                if len(haystack) > 0 and len(needle) <= len(haystack):
                    found = haystack.find(needle) != -1
        return result

    def save_bidders_to_csv(self, bidders: List[str]):
        fname, ext = os.path.splitext(self._fname)
        csv_filename = f"{fname}-bidders.csv"
        with open(csv_filename, "w") as f:
            writer = csv.writer(
                f, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(bidders)


class WorkerThread(Thread):
    def __init__(self, queue: List[str]):
        super().__init__()
        self._q = queue.copy()
        self.start()

    def run(self):
        for idx, val in enumerate(self._q):
            p = Auction46(val)
            t = p.get_txt_from_page(p._pages - 1)
            wx.CallAfter(pub.sendMessage, "update", msg=val)
            wx.GetApp().Yield()
            time.sleep(0.5)
            bidder = p.get_bidders_from_txt(key="is as follows:", txt=t)
            bidder.sort()
            p.save_bidders_to_csv(bidder)
            wx.CallAfter(pub.sendMessage, "update", msg=val)
            wx.GetApp().Yield()


class PDFDropTarget(wx.FileDropTarget):
    def __init__(self):
        super().__init__()

    def OnDropFiles(self, x: int, y: int, filenames: List[str]) -> bool:
        if filenames:
            wx.CallAfter(pub.sendMessage, "work", filenames=filenames)
        return True


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
    app = Auction46App()
    app.MainLoop()
