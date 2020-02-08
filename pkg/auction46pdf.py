#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv

from typing import List
from pkg.pdfdoc import PDFdoc


class Auction46PDF(PDFdoc):
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


if __name__ == "__main__":
    import sys
    print(
        f"{sys.argv[0]} is a module and it is NOT supposed to be called directly!")
