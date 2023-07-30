import time
import logging
from scripts.ssh import SSH



class PingAndPackageLoseTest(object):
    _msg = ""

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)


    def pingPackageLoseTest(self, ssh, addr, count, delay, size):
        self._logger.info("\n\n ###PING AND PACKAGELOSE: " + "Setup settings: count: " + count + " Delay: " + delay + " Msg Size: " + size + " ###")
        self._msg = ""

        if(size == "0"):
            cmd = "ping -c " + count + " -i " + delay + " " + addr
        else:
            cmd = "ping -c " + count + " -i " + delay + " -s " + size + " " + addr
        
        ssh.writeSSH(cmd)
        
        while "rtt min/avg/max/mdev =" not in self._msg:
            time.sleep(0.5)
            self._msg = ssh.readSSH()
            #self._logger.info(str(self._msg))

        self._logger.info("###Result:" + self._msg + "###\n\n")
