import os
import signal
import sys

from twisted.internet import protocol
from twisted.internet import reactor

from maxjob.watcher import create_logfile_watcher


class MaxJobProcessProtocol(protocol.ProcessProtocol):

    def __init__(self):
        self.stdout_history = []
        self.stderr_history = []

    def outReceived(self, data):
        lines = data.split("\n")
        lines = [line.strip() for line in lines]
        lines = filter(lambda line: line != "", lines)
        self.stdout_history.extend(line)
        for line in lines:
            print "stdout:", line

    def errReceived(self, data):
        lines = data.split("\n")
        lines = [line.strip() for line in lines]
        lines = filter(lambda line: line != "", lines)
        self.stderr_history.extend(line)
        for line in lines:
            print "stderr:", line

    def processExited(self, reason):
        print "processExited, status %d" % (reason.value.exitCode,)

    def processEnded(self, reason):
        print "processEnded, status %d" % (reason.value.exitCode,)
        print "quitting"
        reactor.stop()

    # def suicide(self):
    #     self.transport.signalProcess(signal.SIGTERM)
    #     self.transport.signalProcess(signal.SIGKILL)
    #     self.transport.signalProcess("KILL")


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
