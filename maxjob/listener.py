import os
import time

from watchdog import events, observers


class LogFileChangedHandler(events.PatternMatchingEventHandler):
    """Watch a logfile for changes (file must exist).

    We assume that this logfile is only modified in that lines are
    added to it, not modified or removed. This really simplifies the
    diff. Whenever that happens, this handler will notice and notify the
    subscriber(s) via the callback.

    """
    def __init__(self, filepath, callback, *args, **kwargs):
        kwargs["patterns"] = [filepath]  # Watch only that single file.
        super(LogFileChangedHandler, self).__init__(*args, **kwargs)
        self.filepath = filepath
        self.callback = callback
        try:
            self.last_content = open(self.filepath).read().strip()
        except IOError:
            self.last_content = ""

    def on_modified(self, event):
        if event.is_directory:
            return
        with open(event.src_path) as f:
            content = f.read()
        diff = content.replace(self.last_content, "", 1)
        self.last_content = content
        self.callback(diff)


def test():
    maxlogfile = "maxjob.log"
    logfiledir = os.path.dirname(maxlogfile)

    def print_diff(diff):
        if diff:
            print diff

    eventhandler = LogFileChangedHandler(maxlogfile, print_diff)
    observer = observers.Observer()
    observer.schedule(eventhandler, logfiledir)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    test()
