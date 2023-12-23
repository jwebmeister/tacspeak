#
# This file is part of Tacspeak.
# (c) Copyright 2023 by Joshua Webb
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

import os
import sys
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
        dirs.append((distrib.egg_info, os.path.join('Lib', os.path.basename(distrib.egg_info))))
    return dirs

def grammar_modules():
    """
    Gets list of grammar modules (src_dir, dst_dir)
    """
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
include_files.append(("tacspeak/user_settings.py", "tacspeak/user_settings.py"))
include_files.append("README.md")
include_files.append("LICENSE.txt")
include_files.append(("licenses/pkg_licenses_notices.txt", "licenses/pkg_licenses_notices.txt"))
include_files.append(("licenses/pkg_licenses_summary.md", "licenses/pkg_licenses_summary.md"))
include_files.append(("licenses/portaudio_license.txt", "licenses/portaudio_license.txt"))
include_files.append("kaldi_model/")
include_files.append(("kaldi_model/README.md", "kaldi_model/README.md"))
include_files.append(("kaldi_model/user_lexicon.txt", "kaldi_model/user_lexicon.txt"))
include_files.append(("scripts/download_extract_model.ps1", "scripts/download_extract_model.ps1"))
include_files.append(("scripts/move_extracted_model.ps1", "scripts/move_extracted_model.ps1"))
include_files.append(("scripts/compile_dictation_graph.ps1", "scripts/compile_dictation_graph.ps1"))

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
    version="0.1.5",
    description="tacspeak",
    options={"build_exe": build_exe_options},
    executables=[Executable(script="cli.py", 
                            target_name="tacspeak", 
                            copyright="© Copyright 2023 by Joshua Webb"
                            )],
)
