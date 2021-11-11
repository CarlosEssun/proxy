#!/usr/bin/env python
# coding=utf-8 

import time
from loguru import logger
import random, socket
from fasteners.process_lock import InterProcessLock



class BindFreePort(object):
    def __init__(self, start, stop) -> None:
        self.port = None
        self.sock = socket.socket()
        while True:
            self.port = random.randint(start, stop)
            try:
                self.sock.bind(('', self.port))
                break
            except Exception as e:
                logger.error(f"{str(e)}")
                continue

    def release(self) -> None:
        assert self.port is not None
        self.sock.close()

class  FreePort(object):
    used_ports = set()
    def __init__(self,start=4000,stop=6000):
        self.lock = None
        self.bind = None
        self.port = None
        while True:
            bind = BindFreePort(start, stop)
            if bind.port in self.used_ports:
                bind.release()
                continue
            lock = InterProcessLock(path='/var/log/port_{}_lock'.format(bind.port))
            success = lock.acquire(blocking=False)
            if success:
                self.lock = lock
                self.port = bind.port
                self.used_ports.add(bind.port)
                bind.release()
                break
            bind.release()
            time.sleep(0.01)

    def release(self):
        assert self.lock is not None
        assert self.port is not None
        self.used_ports.remove(self.port)
        self.lock.release()
