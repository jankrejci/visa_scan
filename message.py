class Message():

    def __init__(self, src=None, dst=None, cmd=None, args=()):

        self.src = src
        self.dst = dst
        self.cmd = cmd
        self.args = args


    def config(self, src=None, dst=None, cmd=None, args=None):

        if src:
            self.src = src
        if dst:
            self.dst = dst
        if cmd:
            self.cmd = cmd
        if args:
            self.args = args