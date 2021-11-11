#!/usr/bin/env python
# coding=utf-8 

import os
import threading
import paramiko
from tunnel.forward import forward_tunnel
from tunnel.free_port import FreePort


class RemoteTunnel(object):
    """
    跳板隧道
    """
    def __init__(self, *args, **kwargs):
        self.client = None
        self.tunnel = None
        self.freeport = FreePort()
        paramiko.util.log_to_file("/var/log/proxy.log")
        self.transport = paramiko.Transport(
            (kwargs['ssh_host'], kwargs['ssh_port']))
        self.transport.connect(hostkey=None,
                               username=kwargs['ssh_user'],
                               password=kwargs['ssh_password']
                            #    pkey=paramiko.RSAKey.from_private_key_file(
                            #        kwargs.get('password_path',
                            #                   '/tmp/proxy/.ssh/id_rsa'))

                                              )

    def TunnelPort(self, **kwargs):
        self.tunnel = forward_tunnel(self.freeport.port, kwargs['remote_host'],
                                     kwargs['remote_port'], self.transport)
        # print "tunnel",self.tunnel.server_address
        t = threading.Thread(target=self.tunnel.serve_forever)
        t.setDaemon(True)
        t.start()

    def __enter__(self):
        return self

    def __exit__(self, xtype, value, trace):
        self.freeport.release()
        os.remove(self.freeport.lock.path)
        if self.tunnel:
            self.tunnel.socket.close()
