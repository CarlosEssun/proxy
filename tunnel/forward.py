#!/usr/bin/env python
# coding=utf-8 

import select
from loguru import logger
try:
    import SocketServer
except ImportError:
    import socketserver as SocketServer

class ForwardServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

class Handler(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            chan = self.ssh_transport.open_channel(
                "direct-tcpip",
                (self.chain_host, self.chain_port),
                self.request.getpeername(),
            )
        except Exception as e:
            logger.error(f" 创建隧道{self.chain_host}:{self.chain_port}失败:{str(e)}")
            print("进入 request to %s:%d 失败: %s" %
                  (self.chain_host, self.chain_port, repr(e)))
            return
        if chan is None:
            logger.error(f"隧道连接{self.chain_host}:{self.chain_port}被拒绝")
            print("输入 request to %s:%d  SSH server 被拒绝" %
                  (self.chain_host, self.chain_port))
            return
        logger.info(f"隧道连接{self.request.getpeername()}->{chan.getpeername()} ->{(self.chain_host, self.chain_port)} 己打开")
        print("隧道己打开 %r -> %r -> %r" % (
            self.request.getpeername(),
            chan.getpeername(),
            (self.chain_host, self.chain_port),
        ))
        while True:
            r, w, x = select.select([self.request, chan], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                self.request.send(data)

        peername = self.request.getpeername()
        chan.close()
        self.request.close()
        logger.info(f"隧道己关闭{peername}")
        print("隧道己关闭 from %r" % (peername, ))


def forward_tunnel(local_port, remote_host, remote_port, transport):
    class SubHander(Handler):
        chain_host = remote_host
        chain_port = remote_port
        ssh_transport = transport

    #local_port = FreePort().port
    return ForwardServer(("", local_port), SubHander)
