
from zope.interface import implements
from txsshadmin.cred_base import SSHBaseAvatar, SSHBaseRealm
from txsshadmin.proto_dispatcher import (
    makeSSHDispatcherProtocolFactory,
    BaseHandler)
from txsshadmin.service import SSHServiceBase


class DemoHandler(BaseHandler):
    def onConnect(self, dispatcher):
        terminal = dispatcher.terminal
        terminal.write(
            "Welcome to the Demo Service, {0}".format(self.avatar.avatarId))
        terminal.nextLine()


SSHDemoProtocolFactory = makeSSHDispatcherProtocolFactory(DemoHandler)


class SSHDemoAvatar(SSHBaseAvatar):
    protocolFactory = SSHDemoProtocolFactory

    def __init__(self, avatarId):
        SSHBaseAvatar.__init__(self, avatarId)


class SSHDemoRealm(SSHBaseRealm):
   avatarFactory = SSHDemoAvatar 

class SSHDemoService(SSHServiceBase):
    realm = SSHDemoRealm()

