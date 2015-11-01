#!/usr/bin/env python
# :coding: utf-8

import setuptools


setuptools.setup(
    name="maxjob",
    version="0.1.11",
    packages=setuptools.find_packages(),
    install_requires=["pypiwin32", "twisted", "psutil",
                      "easydict", "click", "watchdog"],
    entry_points={"console_scripts": ["maxjob=maxjob.__main__:cli"]}
)
