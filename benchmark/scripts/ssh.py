import paramiko
import time
import logging



class SSH(object):
    _ip = ""
    _port = 0
    _username = ""
    _password = ""

    def __init__(self, ip, port, username, password):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._ip = ip
        self._port = port
        self._username = username
        self._password = password


    def openSSH(self):
        self.client = paramiko.client.SSHClient()     
        self.client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        tryes = 1 
        maxTryes = 60
        self._logger.info("  SSH: connecting to " + str(self._ip) + ", user: " + str(self._username) + ", pass: " + str(self._password) + ", timeout is 60 sek" )

        while(tryes != maxTryes): #How many tryes max
            try:
                self.client.connect(str(self._ip), port = self._port, username=str(self._username), password=str(self._password), timeout=1.0, look_for_keys=False, banner_timeout=5.0)
                self.transport = self.client.get_transport()
                self._logger.info("  SSH: is conneceted")
                break
            except Exception:
                self._logger.info("  SSH: failed to connect to host, retrying again %.0f seconds..." % (tryes))
                time.sleep(1)
                tryes += 1
                if(tryes >= maxTryes + 1):
                    assert("SSH" == "timeout")# Just need a error here

        self._othelloShell = self.client.invoke_shell()
        time.sleep(2)
        msg = self.readSSH()                
        #self._logger.info("Tjecing that target can respond, answer: " + str(msg))
        assert(":~$" in msg)


    def closeSSH(self):
        self.client.close()


    def writeSSH(self, cmd):
        self._othelloShell.send(str(cmd)+"\n")


    def readSSH(self, timeout=2.0):
        """internal method - dont use
        """
        while(timeout > 0.0 and not self._othelloShell.recv_ready()):
            time.sleep(0.1)
            timeout = timeout - 0.1
        
        if(timeout <= 0.0):
            return "No Response"

        response = self._othelloShell.recv(1024)
        
        while self._othelloShell.recv_ready():
            response += self._othelloShell.recv(1024)
        return str(response, "UTF8")



    def avableMsgSSH(self):
        return self._othelloShell.recv_ready()


    def avableSSH(self):
        return self._othelloShell.get_transport().is_active()

    
    def updateMsgSSH(self):
        if(self._othelloShell.recv_ready() == True):
            return self.readSSH()
        else:
            return ""
            

    def deleteFile(self, remoteFile):
        """[summary]
        
        Arguments:
        remoteFile {[type]} -- [description]
        """
        try:
            self._sftp.remove(remoteFile)
        except IOError:
            print("failed removing file: %s", remoteFile)



    def putFile(self, localFile, remoteFile):
        """[summary]
        
        Arguments:
        localFile {[type]} -- [description]
        remoteFile {[type]} -- [description]
        """
        self._sftp.put(localFile, remoteFile)



    def getFile(self, localFile, remoteFile):
        """[summary]
        
        Arguments:
        localFile {[type]} -- [description]
        remoteFile {[type]} -- [description]
        """
        self._sftp.get(remoteFile, localFile)




