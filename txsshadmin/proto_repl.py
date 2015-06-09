#! /usr/bin/env python

from twisted.cred.portal import IRealm, Portal
from twisted.conch.checkers import (
    SSHPublicKeyChecker,
    UNIXAuthorizedKeysFiles)
from twisted.internet import endpoints
from twisted.internet import reactor
from twisted.conch.avatar import ConchUser
from twisted.conch.insults.insults import ServerProtocol
from twisted.conch.interfaces import IConchUser, ISession
from twisted.conch.recvline import HistoricRecvLine
from twisted.conch.ssh.factory import SSHFactory
from twisted.conch.ssh.keys import Key
from twisted.conch.ssh.session import SSHSession, wrapProtocol
from twisted.python import log
from zope.interface import implements
import sys

log.startLogging(sys.stdout)

with open('keys/id_rsa') as privateBlobFile:
    privateBlob = privateBlobFile.read()
    privateKey = Key.fromString(data=privateBlob)

with open('keys/id_rsa.pub') as publicBlobFile:
    publicBlob = publicBlobFile.read()
    publicKey = Key.fromString(data=publicBlob)

class SSHDemoProtocol(HistoricRecvLine):

    prompt = "$"
    CTRL_D = '\x04'

    def __init__(self, avatar):
        self.avatar = avatar

    def connectionMade(self):
        HistoricRecvLine.connectionMade(self)
        self.keyHandlers.update({
            self.CTRL_D: self.handle_EOF})
        self.terminal.write(
            "Welcome, {0}, to the Demo SSH Service".format(self.avatar.avatarId))
        self.terminal.nextLine()
        self.showPrompt()

    def showPrompt(self):
        self.terminal.write("{0} ".format(self.prompt))

    def getCommandFunc(self, cmd):
        return getattr(self, 'handle_{0}'.format(cmd), None)

    def lineReceived(self, line):
        line = line.strip()
        if line:
            argv = line.split()
            cmd = argv[0]
            args = argv[1:]
            func = self.getCommandFunc(cmd)
            if func:
                try:
                    func(*args)
                except Exception as ex:
                    self.terminal.write("Errors occured.")
                    self.terminal.nextLine()
                    log.msg(str(ex))
            else:
                self.terminal.write("Unknown command, '{0}'.".format(cmd))
                self.terminal.nextLine()
        self.showPrompt()

    def handle_help(self): 
        terminal = self.terminal
        terminal.write("Commands: clear help whoami")
        terminal.nextLine()
        
    def handle_whoami(self):
        terminal = self.terminal
        terminal.write("You are '{0}'.".format(self.avatar.avatarId))
        terminal.nextLine()
        
    def handle_clear(self):
        self.terminal.reset()

    def handle_quit(self):
        terminal = self.terminal
        terminal.write("Goodbye.")
        terminal.nextLine()
        terminal.loseConnection()

    def handle_EOF(self):
        if self.lineBuffer:
            self.terminal.write('\a')
        else:
            self.handle_quit()


class SSHDemoAvatar(ConchUser):
    implements(ISession)

    protocol = SSHDemoProtocol

    def __init__(self, avatarId):
        ConchUser.__init__(self)
        self.avatarId = avatarId
        self.channelLookup.update({'session': SSHSession})

    def openShell(self, protocol):
        serverProto = ServerProtocol(self.protocol, self)
        serverProto.makeConnection(protocol)
        protocol.makeConnection(wrapProtocol(serverProto))

    def getPty(self, terminal, windowSize, attrs):
        return None

    def execCommand(self, protocol, cmd):
        raise NotImplementedError("Not implemented.")

    def closed(self):
        pass


class SSHDemoRealm(object):
    implements(IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IConchUser in interfaces:
            return IConchUser, SSHDemoAvatar(avatarId), lambda: None
        else:
            raise Exception("No supported interfaces found.")

factory = SSHFactory()
factory.privateKeys = {'ssh-rsa': privateKey}
factory.publicKeys = {'ssh-rsa': publicKey}
sshRealm = SSHDemoRealm()
sshPortal = Portal(sshRealm)
factory.portal = sshPortal
keydb = UNIXAuthorizedKeysFiles()
factory.portal.registerChecker(SSHPublicKeyChecker(keydb))
ep = endpoints.serverFromString(reactor, 'tcp:2022')
d = ep.listen(factory)
port_info = []

def onListen(port):
    port_info.append(port)
    
d.addCallback(onListen)
reactor.run()
for port in port_info:
    port.stopListening()

