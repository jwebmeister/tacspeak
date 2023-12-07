#
# This file is part of Tacspeak.
# (c) Copyright 2023 by Joshua Webb
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

import os
import sys
from os.path import join, basename
import pkg_resources
from cx_Freeze import setup, Executable

def collect_dist_info(packages):
    """
    Recursively collects the path to the packages' dist-info.
    """
    if not isinstance(packages, list):
        packages = [packages]
    dirs = []
    for pkg in packages:
        distrib = pkg_resources.get_distribution(pkg)
        for req in distrib.requires():
            dirs.extend(collect_dist_info(req.key))
        dirs.append((distrib.egg_info, join('Lib', basename(distrib.egg_info))))
    return dirs

def grammar_modules():
    src_dst_dirs = []

    try:
        path = os.path.dirname(__file__)
    except NameError:
        path = os.getcwd()

    grammar_path = os.path.join(path, os.path.relpath("tacspeak/grammar/"))
    for filename in os.listdir(grammar_path):
        file_path = os.path.abspath(os.path.join(grammar_path, filename))

        # Only apply _*.py to files, not directories.
        is_file = os.path.isfile(file_path)
        if not is_file:
            continue
        if is_file and not (os.path.basename(file_path).startswith("_") and
                            os.path.splitext(file_path)[1] == ".py"):
            continue
        src_dst = (file_path, 
                   os.path.join(os.path.relpath("tacspeak/grammar/"), os.path.basename(file_path))
            )
        src_dst_dirs.append(src_dst)

    return src_dst_dirs

include_files = []
include_files.extend(collect_dist_info("webrtcvad_wheels"))
include_files.extend(grammar_modules())
include_files.append("README.md")
include_files.append("LICENSE.txt")
include_files.append(("licenses/pkg_licenses_notices.txt", "licenses/pkg_licenses_notices.txt"))
include_files.append(("licenses/pkg_licenses_summary.md", "licenses/pkg_licenses_summary.md"))

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["pkg_resources"],
    "include_files": include_files
}

setup(
    name="tacspeak",
    version="0.1",
    description="tacspeak",
    options={"build_exe": build_exe_options},
    executables=[Executable("cli.py")],
)
