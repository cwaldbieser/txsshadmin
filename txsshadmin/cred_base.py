

from twisted.cred.portal import IRealm
from twisted.conch.avatar import ConchUser
from twisted.conch.insults.insults import ServerProtocol
from twisted.conch.interfaces import IConchUser, ISession
from twisted.conch.ssh.session import SSHSession, wrapProtocol
from zope.interface import implements


class ServerProtocol2(ServerProtocol):
    clearOnExist = False

    def loseConnection(self):
        if self.clearOnExit:
            self.reset()
        self.transport.loseConnection()


class SSHBaseAvatar(ConchUser):
    implements(ISession)

    protocolFactory = None
    clearOnExit = False

    def __init__(self, avatarId):
        assert self.protocolFactory is not None, (
            "When subclassing SSHBaseAvatar, set the "
            "`protocolFactory` attribute to a protocol factory`.  "
            "E.g. `SSHDemoProtocolFactory`")
        ConchUser.__init__(self)
        self.avatarId = avatarId
        self.channelLookup.update({'session': SSHSession})

    def openShell(self, protocol):
        serverProto = ServerProtocol2(self.protocolFactory, self)
        serverProto.clearOnExit = self.clearOnExit
        serverProto.makeConnection(protocol)
        protocol.makeConnection(wrapProtocol(serverProto))

    def getPty(self, terminal, windowSize, attrs):
        return None

    def execCommand(self, protocol, cmd):
        raise NotImplementedError("Not implemented.")

    def closed(self):
        pass


class SSHBaseRealm(object):
    implements(IRealm)
    
    avatarFactory = None

    def __init__(self):
        assert self.avatarFactory is not None, (
            "When subclassing `SSHBaseRealm`, set the `avatarFactory` "
            "attribute.  E.g. `SSHDemoAvatar`")

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IConchUser in interfaces:
            return IConchUser, self.avatarFactory(avatarId), lambda: None
        else:
            raise Exception("No supported interfaces found.")

