# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

#
# This file coordinates the deployment of a batch job among toolchain component.
# The geoGen component is included in this release. The run and 
#

from __future__ import absolute_import, division, print_function
from six import iteritems
import qmt as QMT
import os
import sys
import glob
import subprocess
import itertools
from copy import deepcopy
import time

# Spencer: this is fine
class Harness:
    def __init__(self, jsonPath, os=None):
        ''' Class to run a batch 3D job on the cluster. 

            Parameters
            ----------
            jsonPath : str
                Path to the model json file used to build the run
            os : str
                Either 'linux' or 'windows'. The default None detects the OS from sys.platform.
        '''
        try:
            self.jsonPath = os.path.abspath(jsonPath)
        except AttributeError:
            self.jsonPath = jsonPath
        self.model = QMT.Model(self.jsonPath)
        self.modelFilePaths = []
        self.model.loadModel()
        if os is None:
            if 'linux' in sys.platform:
                os = 'linux'
            elif 'win' in sys.platform:
                os = 'windows'
            else:
                raise RuntimeError('Operating system {} is not supported.'.format(sys.platform))
        if os not in ['linux','windows']:
            raise ValueError('os must be either "windows" or "linux"!')
        self.os = os

    @staticmethod
    def convert_unicode_to_ascii(dic):
        '''
        Convert any unicode entries in the dict dic
        '''
        for key, value in dic.iteritems():
            if isinstance(key, unicode) or isinstance(value, unicode):
                newkey = key.encode('ascii','ignore')
                newvalue = value.encode('ascii','ignore')
                del dic[key]
                dic[newkey] = newvalue
        return dic

    def setupRun(self, genModelFiles=True):
        ''' Set up the folder structure of a run, broken out by the geomSweep
            specified in the json file.
        '''
        self.rootPath = self.model.modelDict['jobSettings']['rootPath']
        if not os.path.isdir(self.rootPath):
            os.mkdir(self.rootPath)
        geoSweepKeys = self.model.modelDict['geomSweep'].keys()
        instanceLists = []
        for geoSweepKey in geoSweepKeys:
            numInstances = len(self.model.modelDict['geomSweep'][geoSweepKey]['vals'].split(','))
            valIDs = range(numInstances)
            instanceLists += [valIDs]
        prodInstanceKeys = list(itertools.product(*instanceLists))
        for prodInstance in prodInstanceKeys:
            folderPath = 'geo_' + '_'.join(map(str, list(prodInstance)))
            if not os.path.isdir(self.rootPath + '/' + folderPath):
                os.mkdir(self.rootPath + '/' + folderPath)
            runPath = self.rootPath + '/' + folderPath
            tempModel = QMT.Model(runPath + '/model.json')
            self.modelFilePaths += [runPath + '/model.json']
            tempModel.modelDict = deepcopy(self.model.modelDict)
            tempModel.modelDict['geomSweep'] = {}  # Also reset this
            for index, name in zip(prodInstance, self.model.modelDict['geomSweep'].keys()):
                # Populate the geo parameter names:
                paramName = name
                paramType = self.model.modelDict['geomSweep'][name]['type']  # freeCAD or python
                paramValIndex = index
                paramValsStr = self.model.modelDict['geomSweep'][paramName]['vals']
                paramValsList = paramValsStr.split(',')
                paramVal = paramValsList[paramValIndex]
                tempModel.modelDict['geometricParams'][paramName] = (paramVal, paramType)
                # Populate the geo sweep (just one point, for bookkeeping purposes):
                tempModel.genGeomSweep(paramName, [paramVal], type=paramType)
            tempModel.modelDict['pathSettings']['dirPath'] = runPath
            if genModelFiles:
                tempModel.saveModel()

    def runJob(self):
        ''' Run the batch job.
        '''
        for modelFilePath in self.modelFilePaths:  # For now, this is the serial part
            for jobStep in self.model.modelDict['jobSettings']['jobSequence']:
                if jobStep == 'geoGen':
                    self.runBatchGeoGen(modelFilePath)
                elif jobStep == 'comsolRun':
                    start = time.time()
                    self.runBatchCOMSOLRun(modelFilePath)
                    end = time.time()
                    print('Elapsed time is {0} s.'.format(end - start))
                elif jobStep == 'postProc':
                    self.runBatchPostProc(modelFilePath)
                else:
                    raise ValueError('Job step is not defined!')

    def runBatchGeoGen(self, modelFilePath):
        ''' Run batch geometry generation.
        '''
        # Import the FreeCAD functions we will need:
        import FreeCAD
        from qmt.freecad import modelBuilder, build2DGeo, buildCrossSection

        # Load the model:
        myModel = QMT.Model(modelPath=modelFilePath)
        myModel.loadModel()
        dirPath = myModel.modelDict['pathSettings']['dirPath']
        FCDocPath = myModel.modelDict['pathSettings']['freeCADPath']
        FreeCAD.openDocument(FCDocPath)
        # Build the model
        buildModel = modelBuilder(passModel=myModel)
        for i in range(len(myModel.modelDict['buildOrder'])):
            partName = myModel.modelDict['buildOrder'][str(i)]
            totalParts = len(myModel.modelDict['buildOrder'])
            print('('+str(i+1)+'/'+str(totalParts)+') building part '+partName+'...')
            buildModel.buildPart(partName)
        cadDirPath = dirPath + '/cadParts'
        stlDirPath = dirPath+'/stlParts'
        if not os.path.isdir(cadDirPath):
            os.mkdir(cadDirPath)
        if not os.path.isdir(stlDirPath):
            os.mkdir(stlDirPath)
        buildModel.exportBuiltParts(stepFileDir=dirPath + '/cadParts',stlFileDir=dirPath+'/stlParts')
        buildModel.saveFreeCADState(dirPath+'/freeCADModel.FCStd')
        
        # Now that we have rendered the 3D objects, we want to draw any
        # necessary 2D cross sections as 2D cuts:
        for sliceName, sliceData in iteritems(myModel.modelDict['slices']):
            if sliceData['sliceInfo'].get('crossSection'):
                parts = buildCrossSection(sliceData['sliceInfo'], passModel=myModel)
            else:
                parts = build2DGeo(passModel=myModel)
            sliceData['parts'] = parts

        myModel.saveModel()

    # def runFenics(self, modelFilePath): 
    #     import FreeCAD
    #     import fenics

    #     model = QMT.Model(modelPath=modelFilePath)

    #     FCDocPath = myModel.modelDict['pathSettings']['freeCADPath']

    #     FreeCAD.openDocument(FCDocPath)

    #     part_data = model.modelDict['3DParts']

    #     for part in part_data:

        


        # What do I need to do:
            # First there is some job stuff that maybe can be factored out?
        
        # No equivalent to writing, or compiling,  Comsol java driver
        # don't need MPI launcher hack

        # convert unicode?

        # make output directories (should use python os.path.join)
        # could just make test dirs for now, hack dude!

        # Comsol is invoked via subprocess. So it needs redirect stdout, stderr flags, but with FEniCS we probably
        # want the same redirect behavior--don't know quite how to get in Python
        # Can redirect output resulting from single function call?
        # No worries for now

        # finally awful doneness checking
        # So most of the stuff in this file is just logistics
        # How do the bcs, etc, actually get passed to Comsol?
        # OH! Via the java model.

        # For FEniCS version of this, should not need the step files.
        # And do I need a FEniCS model class? Or can I just read the entries of the dict directly?

        # Let's look through what building the comsol file does, in order:
        # init
            # flags in modelDict['comsolInfo']['physics'] 
            # control whether electrostatics, schroedinger, bdg used
        # write ->
        # build file header
            # creates component, 3D geometry, and mesh as empty objects
            # if necessary, creates other empty things in physics for ES, schroedinger, bdg
        # add 3D parts
            # import, mesh, specify materials and physics (must include BCs)
            # what is build order?
            # for the BCs, check out
                # init physics
                    # sets zero voltage level (model.getSimZero())
                # for each part: (uses part_data, which is modelDict['3DParts'])
                # add material
                    # just adds permittivity
                # add physics 
                    # metal, semiconductor, dielectric
                    # virtual domain?
                    # for each part
                    # boundary conditions in part_data['boundaryCondition'
                    # Lots of complicated other stuff for schroedinger, bdg


        # add study
            # The study is like the things to investigate
            # Also here all the sweeps are added
        # add footer
            # nothing relevant


        # The plan:
        # Let's implement a subset of this functionality
        # Just the metal, zero voltage, and electrostatics...
        # hmm, so my thomas-fermi thing was self consistent SP
        # what does that correspond to here? I'm not sure
        # But let's JUST do electrostatics :D

        









        # objList = FreeCAD.ActiveDocument.Objects

        # shapes = []


        

        



    def runBatchCOMSOLRun(self, modelFilePath):
        ''' Run batch COMSOL run. This requires proprietary components to be 
        installed.
        '''
        import qms
        from qms import comsol
        myModel = QMT.Model(modelPath=modelFilePath)
        myModel.loadModel() # unnecessary
        numNodes = myModel.modelDict['jobSettings']['numNodes']
        numJobsPerNode = myModel.modelDict['jobSettings']['numJobsPerNode']
        numCoresPerJob = myModel.modelDict['jobSettings']['numCoresPerJob']
        numParallelJobs = numNodes*numJobsPerNode
        hostFile = myModel.modelDict['jobSettings']['hostFile']
        comsolExecPath = myModel.modelDict['pathSettings']['COMSOLExecPath']
        comsolCompilePath = myModel.modelDict['pathSettings']['COMSOLCompilePath']
        jdkPath = myModel.modelDict['pathSettings']['jdkPath']
        mpiPath = myModel.modelDict['pathSettings']['mpiPath']
        folder = myModel.modelDict['pathSettings']['dirPath']
        name = myModel.modelDict['comsolInfo']['fileName']
        myComsolModel = comsol.ComsolModel(modelFilePath, run_mode=self.model.modelDict['jobSettings']['comsolRunMode'])

        print('Compiling COMSOL java file...')
        myComsolModel._write()
        if self.os == 'windows':
            compileList = [comsolCompilePath, '-jdkroot', jdkPath, '{0}/{1}.java'.format(folder,name)]
        elif self.os == 'linux':
            compileList = [comsolExecPath, 'compile', '{0}/{1}.java'.format(folder,name)]      
        print('Running '+' '.join(compileList))         
        subprocess.check_call(compileList)  
        
        # If we are on the Linux cluster and not run by SLURM, we need to enable the launcher hack
        slurmRun = self.os == 'linux' and 'SLURM_JOB_NODELIST' in os.environ
        my_env = os.environ.copy()
        if self.os == 'linux' and not slurmRun:
            launcherPath = os.path.dirname(qms.__file__)+'/launch.py'        
            my_env['I_MPI_HYDRA_BOOTSTRAP_EXEC']=launcherPath # for Intel MPI
            my_env['HYDRA_LAUNCHER_EXEC']=launcherPath # for MPICH            
        
        # Convert any unicode entries in the env
        my_env = self.convert_unicode_to_ascii(my_env)

        # Make the export directory if it doesn't exist:
        comsolSolsPath = myModel.modelDict['pathSettings']['dirPath'] + \
                         '/' + myModel.modelDict['comsolInfo']['exportDir']
        if not os.path.isdir(comsolSolsPath):
            os.mkdir(comsolSolsPath)
        if self.os == 'windows':
            comsolModelPath = '\"' + myModel.modelDict['pathSettings'][
                'dirPath'] + '/' + myComsolModel.name + '.class' + '\"'
        elif self.os == 'linux':
            comsolModelPath = myModel.modelDict['pathSettings'][
                'dirPath'] + '/' + myComsolModel.name + '.class'     
        # Initiate the COMSOL run:
        # comsolCommand = [mpiPath, '-n', str(numCores), comsolExecPath, '-nosave', '-np', '1', '-inputFile', comsolModelPath]
        # The above doesn't work with double quotes in the path names
        
        # Note on cores: COMSOL uses the notation "computational node" to specify a shared
        # memory single job. The -np flag is used to set the number of cores used by each, 
        # and it shouldn't exceed the number of physical cores on a machine. Apparently, 
        # the MPI -n flag should be the number of computational nodes, not the number of total
        # cores.'
        comsolLogName = myModel.modelDict['pathSettings']['dirPath'] + '/comsolLog.txt'
        stdOutLogName = myModel.modelDict['pathSettings']['dirPath'] + '/comsolStdOut.txt'
        stdErrLogName = myModel.modelDict['pathSettings']['dirPath'] + '/comsolStdErr.txt'        
        if not self.model.modelDict['jobSettings']['comsolRunMode'] == 'batch': # save the resulting file for manual inspection
            if self.os == 'windows':
                comsolCommand = mpiPath + ' -n ' + str(numParallelJobs) + ' \"' + comsolExecPath +\
                '\" -np ' + str(numCoresPerJob)+ ' -inputFile ' + comsolModelPath
            elif self.os == 'linux':
                comsolCommand = comsolExecPath+' batch -nn '+str(numParallelJobs)+' -nnhost '+str(numJobsPerNode)+\
                                ' -np '+str(numCoresPerJob)+' -inputFile '+comsolModelPath+' -batchlog '+\
                                comsolLogName+' -mpifabrics shm:tcp'
        else:
            if self.os == 'windows':
                comsolCommand = mpiPath + ' -n ' + str(numParallelJobs) + ' \"' + comsolExecPath +\
                '\" -nosave -np ' +str(numCoresPerJob)+ ' -inputFile ' + comsolModelPath
            elif self.os == 'linux':
                comsolCommand = comsolExecPath+' batch -nn '+str(numParallelJobs)+' -nnhost '+str(numJobsPerNode)+\
                                ' -nosave -np '+str(numCoresPerJob)+' -inputFile '+comsolModelPath+' -batchlog '+\
                                comsolLogName+' -mpifabrics shm:tcp'   + ' -mpiarg -verbose'
        # Intel MPI on SLURM needs an extra bootstrap argument
        if slurmRun:
            comsolCommand += ' -mpibootstrap slurm'
                                    
        if hostFile is not None:
            comsolCommand += ' -f '+hostFile
        comsolLog = open(stdOutLogName, 'w')
        comsolErr = open(stdErrLogName, 'w')
        print('Running {} ...'.format(comsolCommand))
        
        comsolRun = subprocess.Popen(comsolCommand, stdout=comsolLog, stderr=comsolErr,shell=True,env=my_env)
        print('Starting COMSOL run...')
        # Determine the number of voltages we are expecting.
        numVoltages = myModel.modelDict['physicsSweep']['length']
        resultFileBase = '{}/{}_export'.format(comsolSolsPath,
                                               myModel.modelDict['comsolInfo']['fileName'])
        eigenFileBase = '{}/{}_eigvals'.format(comsolSolsPath,
                                               myModel.modelDict['comsolInfo']['fileName'])
        surIntFileBase = '{}/{}_sur_integrals'.format(comsolSolsPath,
                                               myModel.modelDict['comsolInfo']['fileName'])
        volIntFileBase = '{}/{}_vol_integrals'.format(comsolSolsPath,
                                               myModel.modelDict['comsolInfo']['fileName'])
        while True:
            if comsolRun.poll() != None:  # If the run is done, tag it as complete
                print('COMSOL run finshed with exit code {}!'.format(comsolRun.returncode))
                break
            else:
                fracComplete = 1.0
                if 'electrostatics' in self.model.modelDict['comsolInfo']['physics']:
                    solsList = glob.glob(resultFileBase + '*.txt')
                    fracComplete = min(len(solsList) / float(numVoltages),fracComplete)
                if ('schrodinger' in self.model.modelDict['comsolInfo']['physics']) or ('bdg' in self.model.modelDict['comsolInfo']['physics']):
                    eigenList = glob.glob(eigenFileBase + '*.txt')
                    fracComplete = min(len(eigenList) / float(numVoltages),fracComplete)
                if self.model.modelDict['comsolInfo']['surfaceIntegrals']:
                    surfIntList = glob.glob(surIntFileBase + '*.txt')
                    fracComplete = min(len(surfIntList) / float(numVoltages),fracComplete)
                if self.model.modelDict['comsolInfo']['volumeIntegrals']:
                    volIntList = glob.glob(volIntFileBase + '*.txt')
                    fracComplete = min(len(volIntList) / float(numVoltages),fracComplete)
                print('... ' + str(fracComplete))
                time.sleep(5.)
                if fracComplete >= 1.0:  # we are done!
                    print('COMSOL run finished, but failed to exit!')
                    print('Closing it in 120 seconds...')
                    sys.stdout.flush()
                    time.sleep(120.)
                    comsolRun.terminate()
                    break
        comsolLog.close()
        comsolErr.close()
                    
    def runBatchPostProc(self, modelFilePath):
        ''' Run batch post-processing. This requires proprietary components
        to be installed.
        '''
        import qms
        numJobsPerNode = self.model.modelDict['jobSettings']['numJobsPerNode']
        numNodes = self.model.modelDict['jobSettings']['numNodes']
        numCores = numNodes*numJobsPerNode                
        mpiexecName = self.model.modelDict['pathSettings']['mpiPath']
        pythonName = self.model.modelDict['pathSettings']['pythonPath']
        hostFile = self.model.modelDict['jobSettings']['hostFile']
        
        # If we are on the Linux cluster and not run by SLURM, we need to enable the launcher hack
        my_env = os.environ.copy()
        if self.os == 'linux' and 'SLURM_JOB_NODELIST' not in os.environ:
            launcherPath = os.path.dirname(qms.__file__)+'/launch.py'        
            my_env['I_MPI_HYDRA_BOOTSTRAP_EXEC']=launcherPath # for Intel MPI            
            my_env['HYDRA_LAUNCHER_EXEC']=launcherPath # for MPICH
        
        # Convert any unicode entries in the env
        my_env = self.convert_unicode_to_ascii(my_env)

        batchPostProcpath = qms.postProcessing.__file__.rstrip('__init__.pyc') + 'batchPostProc.py'
        mpiCmd = [mpiexecName, '-n', str(numCores)]
        if hostFile:
            mpiCmd += ['-f', hostFile]
        pythonCmd = [pythonName, batchPostProcpath, '\"' + modelFilePath + '\"']
        print('Running {}...'.format(mpiCmd + pythonCmd))
        subprocess.check_call(mpiCmd + pythonCmd,env=my_env)
        # subprocess.check_call(' '.join(mpiCmd + pythonCmd))
