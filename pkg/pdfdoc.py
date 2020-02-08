#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import PyPDF4


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
