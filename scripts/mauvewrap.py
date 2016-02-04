import subprocess
import shutil
import os

#This can file can be moved to lib after testing
#These paths can be moved to the settings file after testing
MAUVE_PATH = "/data/Modules/iv-backend/islandviewer_dev/utils/mauve_2.4.0/linux-x64"
MAUVE_OUTPUT_PATH = "/data/Modules/iv-backend/islandviewer/pairwise_mauve"
MAUVE_SCRIPT_BASH_PATH = "/data/Modules/islandviewer4/islandviewer-ui/scripts/mauve-wrapper.sh"

#Parameters = path to 2 genebank files
#Returns None
#Creates an output file at path outputfile and backbone file at path backbonefile
def runMauve(gbk1,gbk2,outputfile=None,outputbackbonefile=None, async=False):
    if outputfile is None:
        outputfile = MAUVE_OUTPUT_PATH+"/"+os.path.splitext(os.path.basename(gbk1))[0]+"-"+os.path.splitext(os.path.basename(gbk2))[0]
    if outputbackbonefile is None:
        outputbackbonefile = MAUVE_OUTPUT_PATH+"/"+os.path.splitext(os.path.basename(gbk1))[0]+"-"+os.path.splitext(os.path.basename(gbk2))[0]

    gbk1temppath = MAUVE_OUTPUT_PATH+"/"+os.path.basename(gbk1)
    gbk2temppath = MAUVE_OUTPUT_PATH+"/"+os.path.basename(gbk2)

    shutil.copyfile(gbk1,gbk1temppath)
    shutil.copyfile(gbk2,gbk2temppath)

    sp = subprocess.Popen(["/bin/bash",MAUVE_SCRIPT_BASH_PATH,outputfile,
                      outputbackbonefile,gbk1temppath,gbk2temppath], cwd=MAUVE_PATH)

    #waits for subprocess to finish if async = False
    if not async:
        sp.wait()

#Given the paths of 2 genebank files, returns path of backbone file if it exists or None if it doesnt
def retrieveBackboneFile(gbk1,gbk2):
    backbonepath = MAUVE_OUTPUT_PATH+"/"+os.path.splitext(os.path.basename(gbk1))[0]+"-"+os.path.splitext(os.path.basename(gbk2))[0]+".backbone"
    if os.path.isfile(backbonepath):
        return backbonepath
    else:
        return None

#Wrapper for retrieving a backbone file. If it doesnt exist, this will call runMauve to create it.
def getMauveResults(gbk1,gbk2):
    if retrieveBackboneFile(gbk1,gbk2) is None:
        runMauve(gbk1,gbk2)
    return retrieveBackboneFile(gbk1,gbk2)


##################### TESTS

def testRunMauve():
    runMauve("/vagrant/islandviewer-ui/scripts/testFiles/AE009952.gbk","/vagrant/islandviewer-ui/scripts/testFiles/BX936398.gbk")

def testRetrieveBackboneFiles():
    print(retrieveBackboneFile("/vagrant/islandviewer-ui/scripts/testFiles/AE009952.gbk","/vagrant/islandviewer-ui/scripts/testFiles/BX936398.gbk"))

def testList():
    #testRunMauve()
    #testRetrieveBackboneFiles()
    print getMauveResults("/vagrant/islandviewer-ui/scripts/testFiles/AE009952.gbk","/vagrant/islandviewer-ui/scripts/testFiles/BX936398.gbk")

#testList()