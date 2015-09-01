from twisted.internet import protocol
from twisted.internet import reactor


class MaxJobProcessProtocol(protocol.ProcessProtocol):

    def __init__(self):
        self.stdout_history = []
        self.stderr_history = []

    def connectionMade(self):
        print "connectionMade!"

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

    def outConnectionLost(self):
        print "outConnectionLost! The child closed their stdout!"
        # (dummy, lines, words, chars, file) = re.split(r'\s+', self.data)

    def errConnectionLost(self):
        print "errConnectionLost! The child closed their stderr."

    def processExited(self, reason):
        print "processExited, status %d" % (reason.value.exitCode,)

    def processEnded(self, reason):
        print "processEnded, status %d" % (reason.value.exitCode,)
        print "quitting"
        reactor.stop()


def main():
    maxbinary = r"C:\Program Files\Autodesk\3ds Max 2015\3dsmax.exe"
    scriptfile = r"C:\Users\Buelter\Google Drive\dev\maxjob\maxjob\backend.ms"
    stdoutfile = r"C:\Users\Buelter\Desktop\stdout.txt"
    # maxlogfile = r"C:\Users\Buelter\Desktop\maxjob.log"

    pp = MaxJobProcessProtocol()
    reactor.spawnProcess(pp,
                         maxbinary,
                         args=["3dsmax.exe", "-U", "MAXScript", scriptfile],
                         env={})
    reactor.run()




if __name__ == '__main__':
    main()