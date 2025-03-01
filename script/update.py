#!/usr/bin/env python3

# Copyright (C) 2021, 2022 Junde Yhi <junde@yhi.moe>
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

# This script extracts necessary language files to the current working
# directory from the latest peazip-x.y.z.about_translations.zip file
# published at <https://github.com/peazip/PeaZip-Translations/releases>.
#
# Run the script under the repository root directory, not the script/
# directory (where this script is placed at).

import io
import json
from pathlib import Path, PurePath
from urllib.request import Request, urlopen
from zipfile import ZipFile

with urlopen(Request(
    'https://api.github.com/repos/peazip/PeaZip-Translations/releases/latest',
    headers={'Accept': 'application/vnd.github.v3+json'}
)) as response:
    latest_releases = json.load(response)

print(f'=> {latest_releases["name"]} published at'
      f'{latest_releases["published_at"]}')

about_translations = [
    asset
    for asset in latest_releases['assets']
    if 'about_translations' in asset['name']
][0]

name = about_translations['name']
url = about_translations['url']

with io.BytesIO() as file_mem:
    with urlopen(
        Request(url, headers={'Accept': 'application/octet-stream'})
    ) as response:
        file_mem.write(response.read())

    # The first level of directory has the same name as the zip file
    base_dir_name = PurePath(name).stem

    file_name_list = [
        'lang/default.txt',
        'lang/chs.txt',

        'lang-wincontext/default.reg',
        'lang-wincontext/chs.reg',
    ]

    Path('lang').mkdir(exist_ok=True)
    Path('lang-wincontext').mkdir(exist_ok=True)

    with ZipFile(file_mem) as zip_file:
        for file_name in file_name_list:
            with zip_file.open(f'{base_dir_name}/{file_name}') as file_in:
                with Path(file_name).open(mode='wb') as file_out:
                    file_out.write(file_in.read())
