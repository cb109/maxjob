#!/usr/bin/env python
# :coding: utf-8

import pip
import setuptools

from setuptools.command.install import install
from setuptools.command.develop import develop


class InstallRequirementsWithPip(install):

    def run(self):
        """Install the requirements via pip directly.

        This is due to install_requires not supporting dependencies that
        point at a github repository, which we use to install a not yet
        released pyinstaller version (3.1.dev0) that has a problem with
        ctypes.util already fixed (which 3.0 still lacks), see:

            https://github.com/pyinstaller/pyinstaller/issues/1623

        """
        pip.main(["install", "-r", "requirements.txt"])
        install.run(self)


class DevelopRequirementsWithPip(develop):
    """Same as InstallRequirementsWithPip, but for the develop command."""

    def run(self):
        pip.main(["install", "-r", "requirements.txt"])
        develop.run(self)


setuptools.setup(
    name="maxjob",
    version="0.1.32",
    description="Start 3ds Max from the commandline to do a maxscript job.",
    long_description=open("README.rst").read(),
    author="Christoph Buelter",
    author_email="info@cbuelter.de",
    url="https://github.com/cb109/maxjob.git",
    keywords="3d, 3dsmax, 3dsmaxcmd, maxscript, dcc, render, batch",
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": [
        "maxjob=maxjob._maxjob:cli"]},
    cmdclass={"install": InstallRequirementsWithPip,
              "develop": DevelopRequirementsWithPip}
)
