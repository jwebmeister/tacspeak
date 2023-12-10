#
# This file is part of Tacspeak.
# (c) Copyright 2023 by Joshua Webb
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

import sys
from os.path import join, basename
from pkg_resources import get_distribution
from cx_Freeze import setup, Executable

def collect_dist_info(packages):
    """
    Recursively collects the path to the packages' dist-info.
    """
    if not isinstance(packages, list):
        packages = [packages]
    dirs = []
    for pkg in packages:
        distrib = get_distribution(pkg)
        for req in distrib.requires():
            dirs.extend(collect_dist_info(req.key))
        dirs.append((distrib.egg_info, join('Lib', basename(distrib.egg_info))))
    return dirs

include_files = []
include_files.extend(collect_dist_info("webrtcvad_wheels"))
include_files.append(("tacspeak/grammar/", "tacspeak/grammar/"))
include_files.append("README.md")
include_files.append("LICENSE.txt")
include_files.append(("licenses/pkg_licenses_notices.txt", "licenses/pkg_licenses_notices.txt"))
include_files.append(("licenses/pkg_licenses_summary.md", "licenses/pkg_licenses_summary.md"))
include_files.append("kaldi_model/")

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": [],
    "include_files": include_files,
    "bin_path_excludes": "C:/Program Files/",
    "excludes": ["tkinter", 
                 "sqlite3",
                 # "asyncio",
                 # "collections",
                 # "concurrent",
                 # "email",
                 # "encodings",
                 # "html",
                 # "http",
                 # "json",
                 # "lib2to3",
                 # "logging",
                 # "multiprocessing",
                 # "pydoc_data",
                 # "pywin",
                 "pip-licenses",
                 "prettytable",
                 # "re",
                 # "test",
                 # "unittest",
                 # "urllib",
                 # "xml",
                 # "xmlrpc",
                 ],
    "include_msvcr": False,
}

setup(
    name="tacspeak",
    version="0.1",
    description="tacspeak",
    options={"build_exe": build_exe_options},
    executables=[Executable("cli.py")],
)
