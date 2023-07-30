import logging
import unittest2
import os


class AutoTest(object):

  def __init__(self):
    self._setupLogger()


  def _setupLogger(self):
    # Set the logger format
    logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
    rootLogger = logging.getLogger()
    rootLogger.setLevel(level=logging.INFO)
    # Add the text file handler
    fileHandler = logging.FileHandler("log.txt", mode='w')
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    # Add the console handler
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    # Save the logger object
    self._logger = logging.getLogger(self.__class__.__name__)



  def executeTests(self, sysArg):
    #Dokumentation on unittest: https://docs.python.org/2/library/unittest.html#loading-and-running-tests
    print("INPUT FROM MAIN: " + str(sysArg))
    self.sysArg = sysArg
    
    stressTestFolder = './testScripts/'
    self._logger.info("Starting stresstest")
    loader = unittest2.TestLoader()
    stressTests = loader.discover(stressTestFolder, top_level_dir=None)
    testRunner = unittest2.runner.TextTestRunner()
    testResult = testRunner.run(stressTests)

    if os.path.exists('testFailed'):
      os.remove('testFailed')

    numberFailed = len(testResult.failures) + len(testResult.errors)
    return numberFailed