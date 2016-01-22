import subprocess
import os

#This can file can be moved to lib after testing
#These paths can be moved to the settings file after testing
MAUVE_PATH = "/home/vagrant/project/chef/cookbooks/baseconfig/files/data/Modules/iv-backend/islandviewer_dev/utils/mauve_2.4.0/linux-x64/"
MAUVE_OUTPUT_PATH = "/vagrant/temp"
MAUVE_SCRIPT_BASH_PATH = "/vagrant/islandviewer-ui/scripts/mauve-wrapper.sh"

#Parameters = path to 2 genebank files
#Returns None
#Creates an output file at path outputfile and backbone file at path backbonefile
def runMauve(outputfile,outputbackbonefile,gbk1,gbk2):
    subprocess.Popen(["/bin/bash",MAUVE_SCRIPT_BASH_PATH,MAUVE_OUTPUT_PATH+"/"+outputfile,
                      MAUVE_OUTPUT_PATH+"/"+outputbackbonefile,gbk1,gbk2], cwd=MAUVE_PATH)

#Given the paths of 2 genebank files, returns path of backbone file if it exists or None if it doesnt
def retrieveBackboneFile(gbk1,gbk2):
    backbonepath = MAUVE_OUTPUT_PATH+"/"+os.path.basename(gbk1)+"-"+os.path.basename(gbk2)+".backbone"
    if os.path.isfile(backbonepath):
        return backbonepath
    else:
        return None

#Wrapper for retrieving a backbone file. If it doesnt exist, this will call runMauve to create it.
def getMauveResults(gbk1,gbk2):
    if retrieveBackboneFile(gbk1,gbk2) is None:
        runMauve(gbk1,gbk2)
    return retrieveBackboneFile(gbk1,gbk2)



# TESTS

def testRunMauve():
    runMauve("testRunMauve","testRunMauve","/vagrant/islandviewer-ui/scripts/testFiles/AE009952.gbk","/vagrant/islandviewer-ui/scripts/testFiles/BX936398.gbk")

def testList():
    testRunMauve()

#testList()