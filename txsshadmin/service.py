
from twisted.application.service import Service
from twisted.cred.portal import Portal
from twisted.conch.checkers import (
    SSHPublicKeyChecker,
    UNIXAuthorizedKeysFiles)
from twisted.conch.ssh.factory import SSHFactory
from twisted.conch.ssh.keys import Key
from twisted.internet import endpoints, reactor


class SSHServiceBase(Service):
    reactor = reactor
    realm = None
    endpointStr = 'tcp:2022'
    servicePrivateKey = 'keys/id_rsa'
    servicePublicKey = 'keys/id_rsa.pub'

    def startService(self):
        assert self.realm is not None, (
            "When subclassing SSHProtoService, assign a realm to the "
            "`realm` attribute (e.g. an instance of `SSHDemoRealm`).")
        with open(self.servicePrivateKey) as privateBlobFile:
            privateBlob = privateBlobFile.read()
            privateKey = Key.fromString(data=privateBlob)
        with open(self.servicePublicKey) as publicBlobFile:
            publicBlob = publicBlobFile.read()
            publicKey = Key.fromString(data=publicBlob)
        factory = SSHFactory()
        factory.privateKeys = {'ssh-rsa': privateKey}
        factory.publicKeys = {'ssh-rsa': publicKey}
        sshRealm = self.realm
        sshPortal = Portal(sshRealm)
        factory.portal = sshPortal
        keydb = UNIXAuthorizedKeysFiles()
        factory.portal.registerChecker(SSHPublicKeyChecker(keydb))
        ep = endpoints.serverFromString(self.reactor, self.endpointStr)
        d = ep.listen(factory)
        self.port_info_ = []
        d.addCallback(self.onListen)

    def onListen(self, port):
        self.port_info_.append(port)
            
    def stopService(self):
        for port in self.port_info_:
            port.stopListening()

