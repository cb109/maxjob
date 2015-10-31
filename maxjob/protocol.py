from twisted.internet import protocol
from twisted.internet import reactor


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
