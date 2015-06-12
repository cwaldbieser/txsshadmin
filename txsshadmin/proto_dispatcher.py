

from twisted.conch.recvline import HistoricRecvLine
from twisted.python import log
from textwrap import dedent

def makeSSHDispatcherProtocolFactory(handlerFactory, *args, **kwds):
    
    def makeDispatcherProtocol(avatar, *a, **k):
        proto = SSHDispatcherProtocol()
        proto.handler = handlerFactory(avatar, *args, **kwds)
        return proto

    return makeDispatcherProtocol


class SSHDispatcherProtocol(HistoricRecvLine):

    prompt = "$"
    CTRL_D = '\x04'

    def connectionMade(self):
        HistoricRecvLine.connectionMade(self)
        self.keyHandlers.update({
            self.CTRL_D: lambda: self.handler.onEOF(self)})
        try:
            self.handler.onConnect(self)
        except AttributeError:
            pass
        self.showPrompt()

    def showPrompt(self):
        self.terminal.write("{0} ".format(self.prompt))

    def getCommandFunc(self, cmd):
        return getattr(self.handler, 'handle_{0}'.format(cmd), None)

    def lineReceived(self, line):
        line = line.strip()
        if line:
            argv = line.split()
            cmd = argv[0]
            args = argv[1:]
            func = self.getCommandFunc(cmd)
            if func:
                try:
                    func(self, *args)
                except Exception as ex:
                    self.terminal.write("Errors occured.")
                    self.terminal.nextLine()
                    log.msg(str(ex))
            else:
                self.terminal.write("Unknown command, '{0}'.".format(cmd))
                self.terminal.nextLine()
        self.showPrompt()


class BaseHandler(object):
    
    def __init__(self, avatar):
        self.avatar = avatar
        commands = [attr[7:] for attr in dir(self) 
            if attr.startswith('handle_') and attr.lower() == attr]
        commands.sort()
        self.commandHelp = "Commands: {0}".format(' '.join(commands))

    def onConnect(self, dispatcher):
        pass

    def handle_help(self, dispatcher, *args): 
        """
        Get help on a command.
        help [COMMAND]
        """
        terminal = dispatcher.terminal
        if len(args) == 0:
            terminal.write(self.commandHelp)
            terminal.nextLine()
            terminal.write("Use `help <command>` for help on a particular command.")
            terminal.nextLine()
        else:
            cmd = args[0]
            handler = "handle_{0}".format(cmd)
            if hasattr(self, handler):
                func = getattr(self, handler)
                doc = dedent(func.__doc__)
                lines = doc.split('\n')
                for line in lines:
                    terminal.write(line)
                    terminal.nextLine()
            else:
                terminal.write("Unknown command, '{0}'.".format(cmd))
                termnial.nextLine()
        
    def handle_whoami(self, dispatcher):
        """
        Show who you are logged in as.
        """
        terminal = dispatcher.terminal
        terminal.write("You are '{0}'.".format(self.avatar.avatarId))
        terminal.nextLine()
        
    def handle_clear(self, dispatcher):
        """
        Clear the terminal.
        """
        terminal = dispatcher.terminal
        terminal.reset()

    def handle_quit(self, dispatcher):
        """
        Exit this admin shell.
        """
        terminal = dispatcher.terminal
        terminal.write("Goodbye.")
        terminal.nextLine()
        terminal.loseConnection()

    def onEOF(self, dispatcher):
        terminal = dispatcher.terminal
        lineBuffer = dispatcher.lineBuffer
        if lineBuffer:
            terminal.write('\a')
        else:
            self.handle_quit(dispatcher)

