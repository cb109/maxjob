#!/usr/bin/env python
# :coding: utf-8

"""Implement the maxjob tool and its commandline interface."""

import click
import logging
import os
import pprint
import Queue

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


class _maxjob(object):
    """Method object to setup and run the tool."""

    def __init__(self):
        self.maxbinary = cfg.paths.max
        self.network_logfile = cfg.paths.networklog
        self.mxs_logfile = cfg.paths.maxscriptlog
        self.timeout = cfg.options.timeout

    def _create_bootstrap_maxscript_line(self):
        """Return a maxscript line to run the needed scripts.
        """
        def wrap(path):
            """Return a path safe to use on the windows cmdline."""
            return os.path.abspath(path).replace("\\", "\\" * 2)

        line = ("fileIn @\"" + wrap(self.backendfile) + "\"; "
                "fileIn @\"" + wrap(self.maxscriptfile) + "\"; ")
        return line.strip()

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

    def setup_files(self, maxscriptfile, scenefile):
        """Prepare the input filepaths."""
        self.maxscriptfile = os.path.abspath(maxscriptfile)
        log.info("maxscript file is:")
        log.info(self.maxscriptfile)

        scenefile = scenefile or ""
        self.scenefile = os.path.abspath(scenefile)
        if scenefile:
            log.info("scenefile is:")
            log.info(self.scenefile)

        self.backendfile = os.path.abspath(
            os.path.join(get_this_directory(unpacked=True), "backend.ms"))

    def setup_messaging(self):
        """Initiate logfile watching and re-logging."""
        self.message_queue = Queue.Queue()
        self.threads = self._create_helper_threads()
        for thread in self.threads:
            log.info("start worker thread: " + str(thread))
            thread.start()

    def _get_default_args(self):
        """Return the 3dsmax.exe default args from the config.

        Here we make sure -mxs is ignored as we add it ourselves.
        Do not fail if the max_default_args option does not exist.

        """
        filtered = []
        try:
            args = cfg.options.max_default_args
        except AttributeError:
            return filtered
        for arg in args:
            if not arg.startswith("-mxs"):
                filtered.append(arg)
        return filtered

    def compose_arguments(self):
        """Compose arguments and log them for debugging."""
        log.info("start max process")
        bootstrap_mxs = self._create_bootstrap_maxscript_line()
        default_args = self._get_default_args()
        self.args = default_args + ["-mxs", bootstrap_mxs]
        if self.scenefile:
            self.args.append(self.scenefile)
        full_maxpath = "\"" + self.maxbinary + "\""
        final_cmdline = full_maxpath + " " + " ".join(self.args)
        log.info("the final commandline is:")
        log.info(final_cmdline)

    def launch_max_process(self):
        """Launch wrapped 3ds Max with the composed arguments."""
        log.info("launch 3ds max")
        protocol = MaxJobProcessProtocol(callback=self._add_to_message_queue,
                                         threads=self.threads)
        self.env = os.environ.update(
            {"MAXJOB_BACKEND_LOGFILE": self.mxs_logfile})
        final_args = (
            [os.path.basename(self.maxbinary)] + self.args)
        self.proc = reactor.spawnProcess(protocol, self.maxbinary,
                                         args=final_args, env=self.env)

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

    def main(self, maxscriptfile, scenefile=""):
        """Facade to setup and run the tool."""
        self.setup_files(maxscriptfile, scenefile)
        # All inputs set, go for it.
        self.setup_messaging()
        self.compose_arguments()
        self.launch_max_process()
        self.setup_process_timeout()
        self.enter_main_loop()


api = _maxjob()


@click.command()
@click.argument("maxscriptfile", type=click.Path(exists=True))
@click.argument("scenefile", type=click.Path(), default="")
@click.option("-v", "--verbose", is_flag=True)
def cli(maxscriptfile, scenefile, verbose):
    """Launch 3ds Max and execute a maxscript file."""
    if verbose:
        log.setLevel(logging.DEBUG)
    log_config()
    api.main(maxscriptfile, scenefile)


if __name__ == '__main__':
    cli()
