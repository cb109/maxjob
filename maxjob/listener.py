import os
import time
import logging

from watchdog import observers
from watchdog import events


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


class MaxLogfileEventHandler(events.PatternMatchingEventHandler):

    def on_any_event(self, event):
        print "something happened:", event


maxlogfile = r"C:\Users\Bueltewwwwr\Desktop\maxjob.log"
logfiledir = os.path.dirname(maxlogfile)

# eventhandler = events.LoggingEventHandler()
# eventhandler = events.PatternMatchingEventHandler(patterns=[maxlogfile])
eventhandler = MaxLogfileEventHandler(patterns=[maxlogfile])

observer = observers.Observer()
observer.schedule(eventhandler, logfiledir)
observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()