#!/usr/bin/env python
# :coding: utf-8

import setuptools


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
    install_requires=open("requirements.txt").readlines(),
    entry_points={"console_scripts": ["maxjob=maxjob._maxjob:cli"]}
)
