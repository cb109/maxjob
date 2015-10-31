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
    log.info("chosen settings:")
    formatted = pprint.pformat(cfg)
    for line in formatted.split("\n"):
        log.info(line)

log_config()


INJECT_MXS_BACKEND_TEMPLATE = """
-- This fileIn() has been injected by the maxjob tool.
-- It is needed to load functionality so we can read the mxs log.
fileIn @"{backendfile}"
"""


def inject_maxscript_backend(maxscriptfile, backendfile, create_copy=True):
    """Add an import and return the script path, since that may differ.

    By default, this is done on a copy of the script so the original is
    not modified. That copy is later used as an argument to 3dsmax.exe.

    """
    def create_copy():
        """Create a copy like from 'myscript.ms' to
        'tmpgz7pir.myscript.ms'in the local appdata directory.
        """
        filename, ext = os.path.splitext(maxscriptfile)
        suffix = "." + os.path.basename(filename) + ext
        workfile_obj = tempfile.NamedTemporaryFile(prefix="maxjob-",
                                                   suffix=suffix, delete=False)
        workfile_obj.close()
        workfile = workfile_obj.name
        with open(maxscriptfile) as src:
            with open(workfile, "w") as dest:
                dest.write(src.read())

        return workfile

    if create_copy:
        maxscriptfile = create_copy()

    with open(maxscriptfile) as f:
        content = f.read()
    header = INJECT_MXS_BACKEND_TEMPLATE.format(backendfile=backendfile)
    new_content = header.strip() + "\n\n\n" + content
    with open(maxscriptfile, "w") as f:
        f.write(new_content)
    return maxscriptfile


@click.command()
@click.argument("maxscriptfile", type=click.Path(exists=True))
@click.argument("scenefile", default="", type=click.Path())
def main(maxscriptfile, scenefile):
    # Get config settings.
    maxbinary = cfg.paths.max
    network_logfile = cfg.paths.networklog
    mxs_logfile = cfg.paths.maxscriptlog
    timeout = cfg.options.timeout

    # Inject maxscript backend into copy of script.
    log.info("injecting maxscript backend import")
    backendfile = os.path.join(get_this_directory(), "backend.ms")
    maxscriptfile = inject_maxscript_backend(maxscriptfile, backendfile)

    # Setup logfile watching and report system.
    message_queue = Queue.Queue()

    def add_to_message_queue(message, prefix=""):
        """Enqueue message, optionally adding a formatted prefix."""
        if prefix:
            prefix = "<{0}> ".format(prefix)
        message_queue.put(prefix + message)

    def create_helper_threads():
        """Return a list of unstarted thread instances."""
        message_writer = MessageQueueWriter(message_queue)
        netlog_watcher = LogFileWatcher(network_logfile, add_to_message_queue,
                                        message_prefix=cfg.prefixes.network)
        mxslog_watcher = LogFileWatcher(mxs_logfile, add_to_message_queue,
                                        message_prefix=cfg.prefixes.mxs)
        return [message_writer, netlog_watcher, mxslog_watcher]

    threads = create_helper_threads()
    for thread in threads:
        log.info("start worker thread: " + str(thread))
        thread.start()

    # Compose arguments and log them for debugging.
    log.info("start max process")
    args = [os.path.basename(maxbinary), "-U", "MAXScript", maxscriptfile]
    if scenefile:
        args.append(scenefile)
    log.info("the final commandline is:")
    log.info(" ".join(args))

    # Launch 3ds Max with twisted.
    protocol = MaxJobProcessProtocol(callback=add_to_message_queue,
                                     threads=threads)
    env = os.environ.update({"MAXJOB_BACKEND_LOGFILE": mxs_logfile})
    proc = reactor.spawnProcess(protocol, maxbinary, args=args, env=env)

    # Forcefully end the process if we reach the timeout.
    killer = TimedProcessKiller(proc.pid, timeout)
    threads.append(killer)
    log.info("start timeout thread: " + str(killer))
    killer.start()

    # Enter main loop.
    log.info("start twisted reactor")
    reactor.run()


if __name__ == '__main__':
    main()
