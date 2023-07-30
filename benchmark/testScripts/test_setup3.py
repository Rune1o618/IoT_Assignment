import logging
import unittest2
from scripts.ssh import SSH
from benchmark.pingAndPackageLoseTest import PingAndPackageLoseTest
from benchmark.bandwidthTest import BandwidthTest


class Test_setup3(unittest2.TestCase):
    _sshIpHost = "77.33.35.35"
    _sshPortHost = 8322
    _sshUser = "iot3"
    _sshPass = "au2021"
    
    _ipReceiver = "fd00:da:fa7:fac:8c0:6e31:9daf:1c53"
    _portReceiver = "22"
    _userReceiver = "iot2"
    _passReceiver = "au2021"



    def test_setup3(self):
        self._logger = logging.getLogger(self.__class__.__name__) 
        self._logger.info("\n\n\n##############-----test_setup3 started-----###################\n")


        try:
            self._logger.info("####---- Node(Sender) <-> Gateway <-> Node(Receiver) \n\n\n")
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