import logging
import unittest2
from scripts.ssh import SSH
from benchmark.pingAndPackageLoseTest import PingAndPackageLoseTest
from benchmark.bandwidthTest import BandwidthTest


class Test_setup4(unittest2.TestCase):
    _sshIpHost = "77.33.35.35"
    _sshPortHost = 8322
    _sshUser = "iot3"
    _sshPass = "au2021"
    
    _ipReceiver = "fd00:da:fa7:fac:a7:64:84.238.78.202"
    _portReceiver = "8091"
    _userReceiver = "iot"
    _passReceiver = "au2021"



    def test_setup4(self):
        self._logger = logging.getLogger(self.__class__.__name__) 
        self._logger.info("\n\n\n##############-----test_setup4 started-----###################\n")


        try:
            self._logger.info("####---- Node(Sender)(IPv6) <-> Host(IPv6->IPv4) <-> Internet <-> Server(Receiver)  \n\n\n")
            ssh = SSH(self._sshIpHost, self._sshPortHost, self._sshUser, self._sshPass)
            ssh.openSSH()
            
            pingAndPackageLoseTest = PingAndPackageLoseTest()
            pingAndPackageLoseTest.pingPackageLoseTest(ssh, self._ipReceiver, "100", "0.2", "0")
            pingAndPackageLoseTest.pingPackageLoseTest(ssh, self._ipReceiver, "100", "0.2", "256")
            pingAndPackageLoseTest.pingPackageLoseTest(ssh, self._ipReceiver, "100", "0.2", "512")

            bandwidthTest = BandwidthTest()
            bandwidthTest.bandwidthTest(ssh, self._ipReceiver, self._portReceiver, self._userReceiver, self._passReceiver, 20.0)

            ssh.closeSSH()
        
        except Exception:
            self._logger.info(str(Exception))
            raise Exception  


        ret = 0
        return ret

if __name__ == '__main__':
    unittest2.main()