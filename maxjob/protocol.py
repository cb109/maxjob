#!/usr/bin/env python
# :coding: utf-8

"""Implement a protocol to handle events for the 3ds Max process."""

from twisted.internet import protocol
from twisted.internet import reactor

from maxjob.config import cfg


class MaxJobProcessProtocol(protocol.ProcessProtocol):
    """Handle process events for 3ds Max.

    The callback is used to put stdout/stderr messages to a queue for
    organized multithreaded logging. When the process is ended, all
    given threads are stopped safely as part of the cleanup.

    """
    def __init__(self, callback=None, threads=None):
        self.callback = callback
        self.threads = threads

    def send_via_callback(self, data, message_prefix=""):
        if not self.callback:
            return
        lines = data.split("\n")
        lines = [line.strip() + "\n" for line in lines if line != ""]
        for line in lines:
            self.callback(line, prefix=message_prefix)

    def cleanup(self):
        if self.threads:
            print("stopping associated helper threads...\n")
            for thread in self.threads:
                print "stop thread:", thread
                thread.stop()
                thread.join()

    def shutdown(self):
        print("quitting...\n")
        self.cleanup()
        reactor.stop()
        print("everything shutdown")

    def outReceived(self, data):
        self.send_via_callback(data, message_prefix=cfg.prefixes.stdout)

    def errReceived(self, data):
        self.send_via_callback(data, message_prefix=cfg.prefixes.stderr)

    def processExited(self, reason):
        print("process exited with status: %d" % (reason.value.exitCode))

    def processEnded(self, reason):
        print("process ended with status: %d" % (reason.value.exitCode))
        self.shutdown()
