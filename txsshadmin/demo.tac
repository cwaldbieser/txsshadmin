
from twisted.application.service import Application
from txsshadmin.demo import SSHDemoService

application = Application("Twisted SSH Service Demo")
service = SSHDemoService()
service.setServiceParent(application)

