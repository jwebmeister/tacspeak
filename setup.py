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

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["pkg_resources"],
    "include_files": collect_dist_info("webrtcvad_wheels")
}

setup(
    name="tacspeak",
    version="0.1",
    description="tacspeak",
    options={"build_exe": build_exe_options},
    executables=[Executable("cli.py")],
)
