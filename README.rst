maxjob
~~~~~~

Start 3ds Max from the commandline to do a job defined by a maxscript file.


Why this tool
-------------

3ds Max is not a great commandline tool for multiple reasons. It returns immediately, leaving us to figure out ourselves when its finished and if it suceeded or failed. The standard output is not redirected to the commandline, nor any other output, like the maxscript log. It is pretty much a black box.

**maxjob** aims at opening this up a bit, by wrapping 3ds Max in a way that you know what it is doing, when it is done or if it crashed. Basically what most rendermanagement systems do in their DCC integrations.

The use case that triggered this tool is unittesting, however it can be used to do anything that you can write as a maxscript.


Dependencies
------------

Lots of, why reinvent the wheel! See *setup.py* > *install_requires*.


Installation
------------

This tool has been created with Python 2.7.
The following steps install the tool from a bash::

    $ cd maxjob
    $ virtualenv venv
    $ . venv/Scripts/activate
    $ python setup.py install


Usage
-----

Modify *maxjob.yml* to your needs, then call::

    $ python -m maxjob [MAXSCRIPTFILE] [SCENEFILE]
