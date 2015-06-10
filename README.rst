
===============================================
Create SSH Server public key / private key pair
===============================================

Example::

    $ ckeygen -b 2048 -t rsa -f keys/id_rsa

=========
Run Demos
=========

Custom protocol over SSH::

    $ twistd -ny ./txsshadmin/proto_service.py

Manhole REPL over SSH::

    $ ./txsshadmin/manhole_repl.py

