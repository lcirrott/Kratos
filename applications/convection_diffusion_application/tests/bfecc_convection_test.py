from __future__ import print_function, absolute_import, division
import KratosMultiphysics as KM
import KratosMultiphysics.KratosUnittest as UnitTest
import KratosMultiphysics.ConvectionDiffusionApplication as CD
import numpy as np
import os

class WorkFolderScope:
    def __init__(self, work_folder):
        self.currentPath = os.getcwd()
        self.scope = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)),work_folder))

    def __enter__(self):
        os.chdir(self.scope)

    def __exit__(self, type, value, traceback):
        os.chdir(self.currentPath)

class BFECCConvectionTest(UnitTest.TestCase):
    def testBFECCConvection(self):
        with WorkFolderScope('BFECCConvectionTest'):
            self.setUp()
            self.runTest()
            self.checkResults()

    def setUp(self):
        self.input_file = "convection_test"
        self.reference_file = "convection_reference"
        self.print_reference_values = False
        self.tolerance = 1e-6

    def runTest(self):
        self.model = KM.Model()
        self.model_part = self.model.CreateModelPart("model_part")
        self.model_part.AddNodalSolutionStepVariable(KM.VELOCITY)
        self.model_part.AddNodalSolutionStepVariable(KM.TEMPERATURE)
        
        model_part_io = KM.ModelPartIO("convection_test")
        model_part_io.ReadModelPart(self.model_part)
        
        self.model_part.SetBufferSize(2)

        self._AssignInitialValues()
        
        locator = KM.BinBasedFastPointLocator2D(self.model_part)
        locator.UpdateSearchDatabase()

        bfecc_utility = CD.BFECCConvection2D(locator)

        self.model_part.CloneTimeStep(0.0)
        self.model_part.CloneTimeStep(2.5)

        substepping = 10
        bfecc_utility.BFECCconvect(self.model_part, KM.TEMPERATURE, KM.VELOCITY, substepping)
        bfecc_utility.ResetBoundaryConditions(self.model_part, KM.TEMPERATURE)
        bfecc_utility.CopyVariableToPreviousTimeStep(self.model_part, KM.TEMPERATURE)

    def checkResults(self):
        if self.print_reference_values:
            with open(self.reference_file+'.csv','w') as ref_file:
                ref_file.write("#ID, TEMPERATURE\n")
                for node in self.model_part.Nodes:
                    value = node.GetSolutionStepValue(KM.TEMPERATURE, 0)
                    ref_file.write("{0}, {1}\n".format(node.Id, value))
        else:
            with open(self.reference_file+'.csv','r') as reference_file:
                reference_file.readline() # skip header
                line = reference_file.readline()
                node_iter = self.model_part.Nodes

                for node in self.model_part.Nodes:
                    values = [ float(i) for i in line.rstrip('\n ').split(',') ]
                    node_id = values[0]
                    reference_value = values[1]

                    value = node.GetSolutionStepValue(KM.TEMPERATURE)
                    self.assertAlmostEqual(reference_value, value, delta=self.tolerance)

                    line = reference_file.readline()
                if line != '': # If we did not reach the end of the reference file
                    self.fail("The number of nodes in the mdpa is smaller than the number of nodes in the output file")

    def _AssignInitialValues(self):
        for node in self.model_part.Nodes:
            node.SetSolutionStepValue(KM.VELOCITY, [1.0, 0.0, 0.0])
            node.SetSolutionStepValue(KM.TEMPERATURE, 1 - np.cos(0.2*np.pi*node.X))

if __name__ == '__main__':
    test = BFECCConvectionTest()
    test.testBFECCConvection()
