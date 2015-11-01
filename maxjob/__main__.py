#!/usr/bin/env python
# :coding: utf-8

"""Implement the maxjob tool and its commandline interface."""

import logging
import os
import pprint
import Queue
import tempfile

import click

from twisted.internet import reactor

from maxjob.config import cfg, get_this_directory
from maxjob.protocol import MaxJobProcessProtocol
from maxjob.workers import (LogFileWatcher, MessageQueueWriter,
                            TimedProcessKiller)


logging.basicConfig(
    format="[%(name)s] - %(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO)
log = logging.getLogger("maxjob")


def log_config():
    """Write settings to stdout for debugging purposes."""
    log.debug("chosen settings:")
    formatted = pprint.pformat(cfg)
    for line in formatted.split("\n"):
        log.debug(line)

log_config()


INJECT_MXS_BACKEND_TEMPLATE = """
-- This fileIn() has been injected by the maxjob tool.
-- It is needed to load functionality so we can read the mxs log.
fileIn @"{backendfile}"
"""


class maxjob(object):
    """Method object to setup and run the tool."""

    def __init__(self):
        self.maxbinary = cfg.paths.max
        self.network_logfile = cfg.paths.networklog
        self.mxs_logfile = cfg.paths.maxscriptlog
        self.timeout = cfg.options.timeout

    def inject_maxscript_backend(self, create_copy=True):
        """Add an import command to the maxscript.

        By default, this is done on a copy of the script so the original is
        not modified. That copy is later used as an argument to 3dsmax.exe.

        """
        def create_copy():
            """Create a copy like from 'myscript.ms' to
            'tmpgz7pir.myscript.ms' in the local appdata directory.
            """
            filename, ext = os.path.splitext(self.maxscriptfile)
            suffix = "." + os.path.basename(filename) + ext
            workfile_obj = tempfile.NamedTemporaryFile(prefix="maxjob-",
                                                       suffix=suffix,
                                                       delete=False)
            workfile_obj.close()
            workfile = workfile_obj.name
            with open(self.maxscriptfile) as src:
                with open(workfile, "w") as dest:
                    dest.write(src.read())

            return workfile

        if create_copy:
            self.maxscriptfile = create_copy()

        with open(self.maxscriptfile) as f:
            content = f.read()
        header = INJECT_MXS_BACKEND_TEMPLATE.format(
            backendfile=self.backendfile)
        new_content = header.strip() + "\n\n\n" + content
        with open(self.maxscriptfile, "w") as f:
            f.write(new_content)

    def _add_to_message_queue(self, message, prefix=""):
        """Enqueue message, optionally adding a formatted prefix."""
        if prefix:
            prefix = "<{0}> ".format(prefix)
        self.message_queue.put(prefix + message)

    def _create_helper_threads(self):
        """Return a list of unstarted thread instances."""
        message_writer = MessageQueueWriter(self.message_queue)
        netlog_watcher = LogFileWatcher(
            self.network_logfile, self._add_to_message_queue,
            message_prefix=cfg.prefixes.network)
        mxslog_watcher = LogFileWatcher(
            self.mxs_logfile, self._add_to_message_queue,
            message_prefix=cfg.prefixes.mxs)
        return [message_writer, netlog_watcher, mxslog_watcher]

    def setup_messaging(self):
        """Initiate logfile watching and re-logging."""
        self.message_queue = Queue.Queue()
        self.threads = self._create_helper_threads()
        for thread in self.threads:
            log.info("start worker thread: " + str(thread))
            thread.start()

    def compose_arguments(self):
        """Compose arguments and log them for debugging."""
        log.info("start max process")
        self.args = [os.path.basename(self.maxbinary),
                     "-U", "MAXScript", self.maxscriptfile]
        if self.scenefile:
            self.args.append(self.scenefile)
        log.info("the final commandline is:")
        log.info(" ".join(self.args))

    def launch_max_process(self):
        """Launch wrapped 3ds Max with the composed arguments."""
        log.info("launch 3ds max")
        protocol = MaxJobProcessProtocol(callback=self._add_to_message_queue,
                                         threads=self.threads)
        self.env = os.environ.update(
            {"MAXJOB_BACKEND_LOGFILE": self.mxs_logfile})
        self.proc = reactor.spawnProcess(protocol, self.maxbinary,
                                         args=self.args, env=self.env)

    def setup_process_timeout(self):
        """Forcefully end the process if we reach the timeout."""
        if self.timeout <= 0:  # User disabled this, do nothing.
            return
        killer = TimedProcessKiller(self.proc.pid, self.timeout)
        self.threads.append(killer)
        log.info("start timeout thread: " + str(killer))
        killer.start()

    def enter_main_loop(self):
        """Start twisted reactor main event loop."""
        log.info("start twisted reactor")
        reactor.run()

    def main(self, maxscriptfile, scenefile):
        """Facade to setup and run the tool."""
        self.maxscriptfile = os.path.abspath(maxscriptfile)
        self.scenefile = scenefile
        self.backendfile = os.path.abspath(
            os.path.join(get_this_directory(unpacked=True), "backend.ms"))
        # All inputs set, go for it.
        self.inject_maxscript_backend()
        self.setup_messaging()
        self.compose_arguments()
        self.launch_max_process()
        self.setup_process_timeout()
        self.enter_main_loop()


api = maxjob()


@click.command()
@click.argument("maxscriptfile", type=click.Path(exists=True))
@click.argument("scenefile", default="", type=click.Path())
def cli(maxscriptfile, scenefile):
    """Launch 3ds Max and execute a maxscript file."""
    api.main(maxscriptfile, scenefile)


if __name__ == '__main__':
    cli()
