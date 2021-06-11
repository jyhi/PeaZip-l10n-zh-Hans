#!/usr/bin/env python3
#
# Script to fetch the latest PeaZip translation files.
# Copyright (C) 2021 Junde Yhi <junde@yhi.moe>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import io
import requests
from argparse import ArgumentParser
from pathlib import Path
from zipfile import ZipFile

argparser = ArgumentParser(description="Fetch the latest translation files from the upstream.", epilog="Note that ./lang/chs.txt and ./lang-wincontext/chs.reg will be overwritten.")
args = argparser.parse_args()

resp_rel = requests.get("https://api.github.com/repos/peazip/PeaZip-Translations/releases/latest", headers={"Accept": "application/vnd.github.v3+json"})
resp_rel.raise_for_status()
rel = resp_rel.json()

print("=> {} published at {}".format(rel["name"], rel["published_at"]))

for asset in rel["assets"]:
  if "about_translations" in asset["name"]:
    url = asset["url"]
    name = asset["name"]

    with io.BytesIO() as file_mem:
      resp_asset = requests.get(url, headers={"Accept": "application/octet-stream"}, stream=True)
      for chunk in resp_asset.iter_content(chunk_size=4096):
        file_mem.write(chunk)

      rootdir = Path(name[:-4]) # XXX: name.removesuffix(".zip")
      txt = Path("lang/chs.txt")
      reg = Path("lang-wincontext/chs.reg")

      file_zip = ZipFile(file_mem)
      for f in [txt, reg]:
        with file_zip.open(str(rootdir / f), "r") as fin:
          with open(str(f), "wb") as fout:
            fout.write(fin.read())
