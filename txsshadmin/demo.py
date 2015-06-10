
from twisted.cred.portal import IRealm
from twisted.conch.avatar import ConchUser
from twisted.conch.insults.insults import ServerProtocol
from twisted.conch.interfaces import IConchUser, ISession
from twisted.conch.ssh.session import SSHSession, wrapProtocol
from zope.interface import implements
from txsshadmin.proto_dispatcher import (
    makeSSHDispatcherProtocolFactory,
    BaseHandler)


class DemoHandler(BaseHandler):
    def onConnect(self, dispatcher):
        terminal = dispatcher.terminal
        terminal.write(
            "Welcome to the Demo Service, {0}".format(self.avatar.avatarId))
        terminal.nextLine()


SSHDemoProtocolFactory = makeSSHDispatcherProtocolFactory(DemoHandler)


class SSHDemoAvatar(ConchUser):
    implements(ISession)

    protocolFactory = SSHDemoProtocolFactory

    def __init__(self, avatarId):
        ConchUser.__init__(self)
        self.avatarId = avatarId
        self.channelLookup.update({'session': SSHSession})

    def openShell(self, protocol):
        serverProto = ServerProtocol(self.protocolFactory, self)
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

