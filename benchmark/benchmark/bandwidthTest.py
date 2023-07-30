import time
import logging
from scripts.ssh import SSH



class BandwidthTest(object):
    _download = 0.0
    _upload = 0.0
    _speed = 0.0
    _msg = ""


    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)



    def bandwidthTest(self, ssh, addr, port, user, password, countRun):
        self._logger.info("\n###Calling BandwidthTest###\n")

        cmd = "scp -P " + port + " TestFileMicro.jpg " + user + "@\[" + addr + "\]:/home/" + user + "/TestFileMicro.jpg"
        
        count = 0.0

        while(count != countRun):
            self._logger.info("Upload:"+str(count+1)+"/"+str(countRun))
            ssh.writeSSH(cmd)
            while "password" not in self._msg:
                time.sleep(0.2)
                self._msg = ssh.readSSH(5.0)
                if "No Response" in self._msg:
                    self._logger.info("No Response at password Restart SSH")
                    ssh.closeSSH()
                    ssh.openSSH()
                    time.sleep(2)
                    self._msg = "100%"
                    break

            ssh.writeSSH(password)
            
            

            while "100%" not in self._msg:
                self._msg = ssh.readSSH(60.0)
                self._logger.info(str(self._msg))
                if("100%" in self._msg): #"KB/s"
                    x1 = self._msg.split("KB/s",1)[0]
                    x2 = x1.split("KB  ",1)[1]
                    self._speed = self._speed + float(x2)
                    count = count + 1.0
                    #self._logger.info(str(self._msg))

                if "No Response" in self._msg:
                    self._logger.info("No Response at scp Restart SSH")
                    ssh.closeSSH()
                    ssh.openSSH()
                    time.sleep(2)
                    self._msg = "100%"
                

        self._upload = self._speed / count
        self._speed = 0.0
        count = 0.0

        cmd = "scp -P " + port + " " + user + "@\[" + addr + "\]:/home/" + user + "/TestFileMicro.jpg /home/iot3/"
        
        while(count != countRun):
            self._logger.info("Download:"+str(count+1)+"/"+str(countRun))
            ssh.writeSSH(cmd)
            while "password" not in self._msg:
                time.sleep(0.2)
                self._msg = ssh.readSSH(5.0)
                if "No Response" in self._msg:
                    self._logger.info("No Response at password Restart SSH")
                    ssh.closeSSH()
                    ssh.openSSH()
                    time.sleep(2)
                    self._msg = "100%"
                    break
            
            ssh.writeSSH(password)

            while "100%" not in self._msg:
                self._msg = ssh.readSSH(60.0)
                self._logger.info(str(self._msg))

                if("100%" in self._msg): #"KB/s"
                    x1 = self._msg.split("KB/s",1)[0]
                    x2 = x1.split("KB  ",1)[1]
                    self._speed = self._speed + float(x2)
                    count = count + 1.0
                    #self._logger.info(str(self._msg))

                if "No Response" in self._msg:
                    self._logger.info("No Response at scp Restart SSH")
                    ssh.closeSSH()
                    ssh.openSSH()
                    time.sleep(2)
                    self._msg = "100%"
                

        self._download = self._speed / count

        self._logger.info("\n###BandwidthTest Result: \n" + "Download: " + str(self._download) + "KB/s , Upload: " + str(self._upload) + "KB/s ###\n\n")
