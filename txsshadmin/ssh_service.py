#! /usr/bin/env python

from twisted.cred.portal import Portal
from twisted.cred.checkers import FilePasswordDB
from twisted.conch.checkers import (
    SSHPublicKeyChecker,
    UNIXAuthorizedKeysFiles)
from twisted.conch.ssh.factory import SSHFactory
from twisted.internet import reactor
from twisted.conch.ssh.keys import Key
from twisted.conch.interfaces import IConchUser
from twisted.conch.avatar import ConchUser
from twisted.conch.ssh.channel import SSHChannel
from twisted.python import log
import sys

log.startLogging(sys.stdout)

with open('keys/id_rsa') as privateBlobFile:
    privateBlob = privateBlobFile.read()
    privateKey = Key.fromString(data=privateBlob)

with open('keys/id_rsa.pub') as publicBlobFile:
    publicBlob = publicBlobFile.read()
    publicKey = Key.fromString(data=publicBlob)

def nothing():
    pass

class SimpleSession(SSHChannel):
    name = 'session'

    def request_pty_req(self, data):
        return True

    def request_shell(self, data):
        return True

    def dataReceived(self, bytes):
        self.write("echo: " + repr(bytes) + "\r\n")

class SimpleRealm(object):
    def requestAvatar(self, avatarId, mind, *interfaces):
        user = ConchUser()
        user.channelLookup['session'] = SimpleSession
        return IConchUser, user, nothing

factory = SSHFactory()
factory.privateKeys = {'ssh-rsa': privateKey}
factory.publicKeys = {'ssh-rsa': publicKey}
factory.portal = Portal(SimpleRealm())
#factory.portal.registerChecker(FilePasswordDB("ssh-passwords"))
keydb = UNIXAuthorizedKeysFiles()
factory.portal.registerChecker(SSHPublicKeyChecker(keydb))

reactor.listenTCP(2022, factory)
reactor.run()
