#!/usr/bin/env python
# coding=utf-8

from loguru import logger
import redis
from tunnel import RemoteTunnel

proxy_config =dict(ssh_host="xx.xx.xx.xx",ssh_port=22,ssh_user="root",ssh_password="dwe5#2")
with RemoteTunnel(**proxy_config)  as rt:
  rt.TunnelPort(remote_host="host",remote_port=111111)
  _, port = rt.tunnel.server_address
  proxy_config.update({"port": port,"password":"passwd"})

  try:
     rclient = redis.StrictRedis(host=proxy_config.get("host","127.0.0.1"),port=proxy_config.get('port', 6379),db=0,password=proxy_config['password'],errors='strict')
     print(rclient.info())
  except Exception as e:
     pass
