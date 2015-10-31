import logging
import os
import Queue

from twisted.internet import reactor

from maxjob.protocol import MaxJobProcessProtocol
from maxjob.workers import (LogFileWatcher, MessageQueueWriter,
                            TimedProcessKiller)


logging.basicConfig(
    format="[%(name)s] - %(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)
log = logging.getLogger("maxjob")


def main():
    timeout = 3600  # In seconds, == 1 h.
    maxbinary = r"C:\Program Files\Autodesk\3ds Max 2015\3dsmax.exe"
    maxjob_backend = r"C:\Users\Buelter\Google Drive\dev\maxjob\maxjob\backend.ms"

    network_logfile = r"C:\Users\Buelter\AppData\Local\Autodesk\3dsMax\2015 - 64bit\ENU\Network\Max.log"
    mxs_logfile = os.path.abspath("maxjob.log")

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
                                        message_prefix="network")
        mxslog_watcher = LogFileWatcher(mxs_logfile, add_to_message_queue,
                                        message_prefix="mxs")
        return [message_writer, netlog_watcher, mxslog_watcher]

    # Thread references are also used in the reactor cleanup later.
    threads = create_helper_threads()
    for thread in threads:
        log.info("start worker thread: " + str(thread))
        thread.start()

    # Launch 3ds Max and listen to its standard channels.
    log.info("start max process")
    protocol = MaxJobProcessProtocol(callback=add_to_message_queue,
                                     threads=threads)
    args = [os.path.basename(maxbinary), "-U", "MAXScript", maxjob_backend]
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


"""

inject via copying backend-load script to early startup location?
or by creating a copy of the wanted script and adding a filein on top (log that)?

"""
