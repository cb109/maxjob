import os
import psutil
import Queue
import signal
import sys
import threading
import time

from watchdog import events, observers


class _LogFileChangedHandler(events.PatternMatchingEventHandler):
    """Watch a logfile for changes (file must exist).

    We assume that this logfile is only modified in that lines are
    added to it, not modified or removed. This really simplifies the
    diff. Whenever that happens, this handler sends the diff through the
    callback function.

    """
    def __init__(self, filepath, callback, message_prefix="", *args, **kwargs):
        kwargs["patterns"] = [filepath]  # Watch only that single file.
        super(_LogFileChangedHandler, self).__init__(*args, **kwargs)
        self.filepath = filepath
        self.callback = callback
        self.message_prefix = message_prefix
        try:
            self.last_lines = open(self.filepath).readlines()
        except IOError:
            self.last_lines = []

    def on_modified(self, event):
        if event.is_directory:
            return
        with open(event.src_path) as f:
            lines = f.readlines()
        num_lines = len(lines)
        num_last_lines = len(self.last_lines)
        unchanged = num_lines == num_last_lines
        subtracted = num_lines < num_last_lines
        added = (not unchanged) and (not subtracted)
        if added:
            diff_lines = lines[len(self.last_lines):]
            for line in diff_lines:
                self.callback(line, prefix=self.message_prefix)
        self.last_lines = lines


def LogFileWatcher(filepath, callback, message_prefix=""):
    """Return a watchdog thread that reacts to file modification.
    """
    logfiledir = os.path.dirname(filepath)
    handler = _LogFileChangedHandler(filepath, callback, message_prefix)
    observer = observers.Observer()
    observer.schedule(handler, logfiledir)
    return observer


class _BaseThread(threading.Thread):
    """A thread that can be stopped gracefully."""

    def __init__(self, *args, **kwargs):
        super(_BaseThread, self).__init__(*args, **kwargs)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    @property
    def stopped(self):
        return self._stop.isSet()


class MessageQueueWriter(_BaseThread):
    """Writes message from a queue to stdout in order."""

    def __init__(self, queue, *args, **kwargs):
        super(MessageQueueWriter, self).__init__(*args, **kwargs)
        self.queue = queue

    def run(self):
        while not self.stopped:
            try:
                # An empty queue would make us wait forever if blocked.
                message = self.queue.get(block=False)
            except Queue.Empty:
                pass
            else:
                sys.stdout.write(message)
                sys.stdout.flush()


class TimedProcessKiller(_BaseThread):
    """Kill given process by id when timeout is reached.

    This thread stings the watched process like a bee and dies with it.
    An interval can optionally be passed. All timings are in seconds.

    """
    def __init__(self, pid, timeout, *args, **kwargs):
        super(TimedProcessKiller, self).__init__(*args, **kwargs)
        self.pid = pid
        self.timeout = timeout
        self.interval = kwargs.get("interval", 0.25)

    @property
    def process_alive(self):
        return psutil.pid_exists(self.pid)

    @property
    def timeout_reached(self):
        self.timeout -= self.interval
        return self.timeout <= 0

    def kill_process(self):
        os.kill(self.pid, signal.SIGTERM)

    def run(self):
        while not self.stopped:
            time.sleep(self.interval)
            if not self.process_alive:
                self.stop()
            if self.timeout_reached:
                self.kill_process()
                self.stop()


def test():
    def print_diff(diff):
        if diff:
            print diff
    logfile = os.path.abspath("maxjob.log")
    watcher = LogFileWatcher(logfile, print_diff)
    watcher.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
    watcher.join()


if __name__ == '__main__':
    test()
