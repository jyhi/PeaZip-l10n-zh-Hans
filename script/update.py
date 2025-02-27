#!/usr/bin/env python3
#
# Script to fetch the latest PeaZip translation files.
# Copyright (C) 2021, 2022 Junde Yhi <junde@yhi.moe>
# Copyright (C) 2024 yangyangdaji <1504305527@qq.com>
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
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

# Initialize argument parser
argparser = ArgumentParser(
    description="Fetch the latest translation files from the upstream.",
    epilog="Files will be overwritten."
)
args = argparser.parse_args()

try:
    # Fetch latest release metadata from GitHub API
    resp_rel = requests.get(
        "https://api.github.com/repos/peazip/PeaZip-Translations/releases/latest",
        headers={"Accept": "application/vnd.github.v3+json"}
    )
    resp_rel.raise_for_status()
    rel = resp_rel.json()

    print(f"=> {rel['name']} published at {rel['published_at']}")

    # Process each asset in the release
    for asset in rel["assets"]:
        if "about_translations" in asset["name"]:
            url = asset["url"]
            name = asset["name"]

            # Download and load ZIP into memory
            with io.BytesIO() as file_mem:
                resp_asset = requests.get(
                    url,
                    headers={"Accept": "application/octet-stream"},
                    stream=True
                )
                resp_asset.raise_for_status()
                
                # Stream download to avoid loading entire file into memory
                for chunk in resp_asset.iter_content(chunk_size=16384):
                    file_mem.write(chunk)

                rootdir = Path(name).stem  # Remove .zip extension

                # Define target paths
                lang_dir = Path("lang")
                lang_wincontext_dir = Path("lang-wincontext")
                target_files = [
                    lang_dir / "default.txt",
                    lang_wincontext_dir / "default.reg",
                    lang_dir / "chs.txt",
                    lang_wincontext_dir / "chs.reg"
                ]

                # Extract files from ZIP
                file_zip = ZipFile(file_mem)
                
                # Write extracted files to local directories
                for f in target_files:
                    try:
                        # Convert Windows paths to POSIX format for ZIP internal structure
                        zip_path = PurePosixPath(rootdir) / str(f).replace("\\", "/")
                        
                        with file_zip.open(str(zip_path), "r") as fin:
                            # Ensure parent directory exists
                            f.parent.mkdir(parents=True, exist_ok=True)
                            
                            with open(f, "wb") as fout:
                                fout.write(fin.read())
                    except KeyError as e:
                        print(f"Error: {e}. File not found in the ZIP archive.")

except requests.RequestException as e:
    print(f"Network error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
