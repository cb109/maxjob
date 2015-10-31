import os
import signal
import sys

from twisted import reactor

from maxjob.watcher import create_logfile_watcher
from maxjob.protocol import MaxJobProcessProtocol


def test():
    maxbinary = r"C:\Program Files\Autodesk\3ds Max 2015\3dsmax.exe"
    maxjob_backend = r"C:\Users\Buelter\Google Drive\dev\maxjob\maxjob\backend.ms"

    network_logfile = r"C:\Users\Buelter\AppData\Local\Autodesk\3dsMax\2015 - 64bit\ENU\Network\Max.log"
    mxs_logfile = os.path.abspath("maxjob.log")

    def print_diff(diff):
        if diff:
            print diff

    # Observe logfiles for changes.
    watchers = [create_logfile_watcher(network_logfile, print_diff),
                create_logfile_watcher(mxs_logfile, print_diff)]
    for watcher in watchers:
        watcher.start()

    # Launch 3ds Max and listen to its standard channels.
    protocol = MaxJobProcessProtocol()
    args = ["3dsmax.exe", "-U", "MAXScript", maxjob_backend]
    env = os.environ.update({"MAXJOB_BACKEND_LOGFILE": mxs_logfile})

    # def register_interrupt_handler():
    #     def cleanup(signal_, frame):
    #         print "Performing cleanup work, hang on..."
    #         protocol.suicide()
    #         reactor.stop()
    #         for watcher in watchers:
    #             watcher.stop()
    #         sys.exit(0)
    #     signal.signal(signal.SIGINT, cleanup)

    # register_interrupt_handler()

    reactor.spawnProcess(protocol, maxbinary, args=args, env=env)
    reactor.run()


if __name__ == '__main__':
    test()
