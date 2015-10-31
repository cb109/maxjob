import setuptools


setuptools.setup(name="maxjob",
                 version="0.1.1",
                 packages=setuptools.find_packages(),
                 install_requires=["pypiwin32",
                                   "twisted",
                                   "psutil",
                                   "easydict",
                                   "click",
                                   "watchdog"])
