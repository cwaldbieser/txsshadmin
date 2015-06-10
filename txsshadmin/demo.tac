
from twisted.application.service import Application
from txsshadmin.proto_service import SSHProtoService

application = Application("Twisted SSH Service Demo")
service = SSHProtoService()
service.setServiceParent(application)

