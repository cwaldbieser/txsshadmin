################################################################
Administrative Services Over SSH for Twisted Python Applications
################################################################

===============================================
Create SSH Server public key / private key pair
===============================================

Example::

    $ mkdir keys
    $ ckeygen -b 2048 -t rsa -f keys/id_rsa

=========
Run Demos
=========

Custom protocol over SSH::

    $ twistd -ny ./txsshadmin/demo.tac

Manhole REPL over SSH::

    $ ./txsshadmin/manhole_repl.py


===========================
Create Your Own SSH Service
===========================

-------------------------
Create a Protocol Handler
-------------------------

Subclass `txsshadmin.proto_dispatcher.BaseHandler`.  Override handler methods
you wish to customize.  When the handler is created, the SSH avatar is assigned 
to its `avatar` attribute.  Each handler method is passed an instance of the dispatcher.

-------------------------
Create a Protocol Factory
-------------------------

Use `txsshadmin.proto_dispatcher.makeSSHDispatcherProtocolFactory()` to create
a protocol factory from your handler.

--------------------
Create an SSH Avatar
--------------------

Subclass `txsshadmin.cred_base.SSHBaseAvatar` to create an avatar for your
ssh service.  Assign the protocol factory you created to its `protocolFactory`
attribute.  The avatar is where you can define the capabilities of authenticated
users.  A protocol handler for a service with users with various capabilities
may delegate its handlers to its avatar.

--------------
Create a Realm
--------------

The realm determines what avatar (if any) is returned when the authenticated 
avatar ID and a list of interfaces is provided to the realm.  The resulting
avatar should support at least one of the provided interfaces.

For a simple realm that returns only a single type of avatar, you can subclass
`txsshadmin.cred_base.SSHBaseRealm` and set the `avatarFactory` attribute to
an avatar factory.  For more sophisticated realms, you can include logic that
returns different avatars based on capabilities keyed to the avatar ID.

----------------------
Create the SSH Service
----------------------

Subclass `txsshadmin.service.SSHServiceBase`.  Set the `realm` attribute equal
to an instance of your realm.  


