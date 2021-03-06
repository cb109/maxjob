maxjob
~~~~~~

Start 3ds Max from the commandline to do a maxscript job.


Why this tool
-------------

3ds Max is not a great commandline tool for multiple reasons. It returns immediately, leaving us to figure out ourselves when it iss finished and if it suceeded or failed. The standard output is not redirected to the commandline, nor any other output, like the maxscript log. It is pretty much a black box.

maxjob aims at opening this up a bit, by wrapping 3ds Max in a way that you know what it is doing, when it is done and if it crashed. Basically what most rendermanagement systems do in their DCC integrations.

The use case that triggered this tool is unittesting, however it can be used to do anything that you can write as a maxscript.


Usage
-----

Modify *maxjob.yml* to your needs, then call::

    $ maxjob [MAXSCRIPTFILE] [SCENEFILE]


Configuration
-------------

You can change the 3ds Max version and other settings in the *maxjob.yml*.

- *paths.max*: The path to the 3dsmax.exe you want to use.
- *paths.networklog*: The path to the default network logfile. Must match the version.
- *paths.maxscriptlog*: The path where maxjob redirects the maxscript log into. You need write rights at that location.
- *options.timeout*: A time in seconds after which the 3dsmax.exe is forcefully terminated. **THIS IS POTENTIALLY DANGEROUS IF YOU ARE RENDERING INTO AN IMAGE OR SAVING FILES TO DISK!**. Disable it by setting it to a negative number. Disabled by default.
- *options.max_default_args*: To disable all default arguments, simply remove the *max_default_args* option.
- *prefixes*: Each log message is prefixed with its original source as specified here.


Known Limitations
-----------------

- By default, maxjob launches 3ds Max like a user would which consumes a license. You can configure it to launch in '-server' mode instead, but this will take away the maxscript log from the output (the most interesting part of it).
- maxjob uses the *-mxs* flag internally, which will **shutdown** 3ds Max after the script has been executed.
- The maxscript log is redirected from inside 3ds Max using *openLog <mxs.log>*. Since this is limited to one file at a time, you cannot use it in your own scripts without taking away the maxscript log from maxjob.

Installation
------------

This tool has been created with Python 2.7.
The following steps install the tool from a bash::

    $ cd maxjob
    $ virtualenv venv
    $ . venv/Scripts/activate
    $ python setup.py install


Build
-----

The tool can be build into a single *maxjob.exe*::

    $ . build.sh

The *maxjob.yml* must reside next to the *maxjob.exe*.


Dependencies
------------

Lots of, why reinvent the wheel! See *requirements.txt*.


Test
----

You need 3ds Max installed and its path configured in the *maxjob.yml*::

    py.test tests -v [-s]


ToDo
----

- Add support for python scripts.
- Think about configuration via cmdline args, env vars etc.
- Try to find sane defaults like the max version e.g. by looking at the registry.
- All output should probably be put in a file by default.
- Use logging everywhere, probably also for logging to file and handling the queue.
