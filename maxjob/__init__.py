import os
import Queue

from twisted.internet import reactor

from maxjob.workers import (LogFileWatcher, MessageQueueWriter,
                            TimedProcessKiller)
from maxjob.protocol import MaxJobProcessProtocol


def test():
    timeout = 3600  # In seconds, == 1 h.
    maxbinary = r"C:\Program Files\Autodesk\3ds Max 2015\3dsmax.exe"
    maxjob_backend = r"C:\Users\Buelter\Google Drive\dev\maxjob\maxjob\backend.ms"

    network_logfile = r"C:\Users\Buelter\AppData\Local\Autodesk\3dsMax\2015 - 64bit\ENU\Network\Max.log"
    mxs_logfile = os.path.abspath("maxjob.log")

    message_queue = Queue.Queue()

    def add_to_message_queue(message, prefix=""):
        message_queue.put(prefix + message)

    threads = [MessageQueueWriter(message_queue),
               LogFileWatcher(network_logfile, add_to_message_queue, message_prefix="[net] "),
               LogFileWatcher(mxs_logfile, add_to_message_queue, message_prefix="[mxs] ")]
    for thread in threads:
        thread.start()

    # Launch 3ds Max and listen to its standard channels.
    protocol = MaxJobProcessProtocol(callback=add_to_message_queue,
                                     threads=threads)
    args = [os.path.basename(maxbinary), "-U", "MAXScript", maxjob_backend]
    env = os.environ.update({"MAXJOB_BACKEND_LOGFILE": mxs_logfile})

    # Forcefully end the process if we reach the timeout.
    print "start max process"
    proc = reactor.spawnProcess(protocol, maxbinary, args=args, env=env)

    killer = TimedProcessKiller(proc.pid, timeout)
    threads.append(killer)
    killer.start()

    print "start reactor"
    reactor.run()


if __name__ == '__main__':
    test()

# import threading
# import sys
# import time


# class Filler(threading.Thread):

#     def __init__(self, queue, interval, prefix, *args, **kwargs):
#         super(Filler, self).__init__(*args, **kwargs)
#         self.queue = queue
#         self.interval = interval
#         self.prefix = prefix

#     def run(self):
#         while True:
#             time.sleep(self.interval)
#             self.queue.put(self.prefix + str(time.time()) + "\n")


# class Writer(threading.Thread):

#     def __init__(self, queue, *args, **kwargs):
#         super(Writer, self).__init__(*args, **kwargs)
#         self.queue = queue

#     def run(self):
#         while True:
#             message = self.queue.get()
#             if message:
#                 sys.stdout.write(message)
#                 sys.stdout.flush()

# q = Queue.Queue()
# q.put("foo\n")
# q.put("bar\n")
# q.put("test\n")

# f1 = Filler(q, 1, "f1")
# f2 = Filler(q, 0.1, "f2")
# f1.start()
# f2.start()

# w = Writer(q)
# w.start()
# w.join()


"""

inject via copying backend-load script to early startup location?
or by creating a copy of the wanted script and adding a filein on top (log that)?


http://twistedmatrix.com/pipermail/twisted-python/2004-February/007050.html

> as processProtocol.transport.pid.  You can use
> reactor.callLater to set up a
> simple timeout so that processes are killed if they run for too long.

# def register_interrupt_handler(proc):
#     signal.signal(signal.SIGINT, cleanup)
# register_interrupt_handler(proc)

def patch_reactor_sigint(reactor):
    original_reactor = reactor

    def patched_run(*args, **kwargs):
        original_reactor.startRunning(*args, **kwargs)

        def cleanup():
            print "Performing cleanup work, hang on..."
            kill_process(proc.pid)
            reactor.callFromThread(reactor.stop())
            for logwatcher in logwatchers:
                logwatcher.stop()
        signal.signal(signal.SIGINT, cleanup)
        original_reactor.mainLoop()
    reactor.run = patched_run

patch_reactor_sigint(reactor)

"""
