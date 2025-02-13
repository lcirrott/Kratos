from __future__ import print_function, absolute_import, division
import KratosMultiphysics

import KratosMultiphysics.StructuralMechanicsApplication as StructuralMechanicsApplication
import KratosMultiphysics.KratosUnittest as KratosUnittest
import KratosMultiphysics.kratos_utilities as kratos_utils
from KratosMultiphysics.StructuralMechanicsApplication import postprocess_eigenvalues_process
from KratosMultiphysics.compare_two_files_check_process import CompareTwoFilesCheckProcess

import os

def GetFilePath(fileName):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), fileName)

def CreateNodes(model_part):
    model_part.CreateNewNode(1, -0.5, - 0.45,  0.1)
    model_part.CreateNewNode(2,  0.7,  -0.5,   0.2)
    model_part.CreateNewNode(3,  0.55,  0.6,   0.15)
    model_part.CreateNewNode(4, -0.48,  0.65,  0.0)
    model_part.CreateNewNode(5,  0.02, -0.01, -0.15)
    model_part.CreateNewNode(6, -0.03, -0.5,   0.0)
    model_part.CreateNewNode(7,  0.51,  0.02,  0.03)
    model_part.CreateNewNode(8, -0.01,  0.52, -0.05)
    model_part.CreateNewNode(9, -0.49, -0.0,   0.0)

def GetEigenValueVector(num_eigenvalues):
    # this function creates "random" eigenvalues
    eigenval_vector = KratosMultiphysics.Vector(num_eigenvalues)

    for i in range(num_eigenvalues):
        eigenval_vector[i] = (i*5+9.333)**5.234

    return eigenval_vector

def GetEigenVectorMatrix(num_eigenvalues, node_id):
    # this function creates "random" eigenvectors based on the node id
    eigenvec_matrix = KratosMultiphysics.Matrix(num_eigenvalues, 6)

    for i in range(num_eigenvalues):
        for j in range(6):
            eigenvec_matrix[i,j] = ((node_id+1)**(i+0.258) + 5)/(j+2.2)

    return eigenvec_matrix

def ExecuteTestPostprocessEigenvaluesProcess(eigen_post_parameters, test_model):
    model_part = test_model.CreateModelPart("Structure")

    model_part.AddNodalSolutionStepVariable(KratosMultiphysics.DISPLACEMENT)
    model_part.AddNodalSolutionStepVariable(KratosMultiphysics.REACTION)
    model_part.AddNodalSolutionStepVariable(KratosMultiphysics.ROTATION)
    model_part.AddNodalSolutionStepVariable(KratosMultiphysics.REACTION_MOMENT)

    model_part.ProcessInfo[KratosMultiphysics.STEP] = 15

    CreateNodes(model_part)

    # adding dofs is needed for the process internally
    KratosMultiphysics.VariableUtils().AddDof(KratosMultiphysics.DISPLACEMENT_X, KratosMultiphysics.REACTION_X, model_part)
    KratosMultiphysics.VariableUtils().AddDof(KratosMultiphysics.DISPLACEMENT_Y, KratosMultiphysics.REACTION_Y, model_part)
    KratosMultiphysics.VariableUtils().AddDof(KratosMultiphysics.DISPLACEMENT_Z, KratosMultiphysics.REACTION_Z, model_part)
    KratosMultiphysics.VariableUtils().AddDof(KratosMultiphysics.ROTATION_X, KratosMultiphysics.REACTION_MOMENT_X,model_part)
    KratosMultiphysics.VariableUtils().AddDof(KratosMultiphysics.ROTATION_Y, KratosMultiphysics.REACTION_MOMENT_Y,model_part)
    KratosMultiphysics.VariableUtils().AddDof(KratosMultiphysics.ROTATION_Z, KratosMultiphysics.REACTION_MOMENT_Z,model_part)


    # set EigenValues and -Vectors
    num_eigenvalues = 4
    eigenval_vector = GetEigenValueVector(num_eigenvalues)
    model_part.ProcessInfo[StructuralMechanicsApplication.EIGENVALUE_VECTOR] = eigenval_vector

    for node in model_part.Nodes:
        node.SetValue(StructuralMechanicsApplication.EIGENVECTOR_MATRIX,
                        GetEigenVectorMatrix(num_eigenvalues, node.Id))

    # Use the process
    post_eigen_process = postprocess_eigenvalues_process.Factory(eigen_post_parameters, test_model)

    post_eigen_process.ExecuteInitialize()
    post_eigen_process.ExecuteBeforeSolutionLoop()
    post_eigen_process.ExecuteInitializeSolutionStep()
    post_eigen_process.ExecuteFinalizeSolutionStep()
    post_eigen_process.ExecuteBeforeOutputStep()
    post_eigen_process.ExecuteAfterOutputStep()
    post_eigen_process.ExecuteFinalize()


class TestPostprocessEigenvaluesProcess(KratosUnittest.TestCase):
    def tearDown(self):
        kratos_utils.DeleteFileIfExisting("Structure_EigenResults_15_0.post.msh")
        kratos_utils.DeleteFileIfExisting("Structure_EigenResults_15_0.post.res") # usually this is deleted by the check process but not if it fails

    def test_PostprocessEigenvaluesProcess_GiD(self):
        # here the minimum settings are specified to test the default values!
        settings_eigen_process = KratosMultiphysics.Parameters("""{
            "Parameters" : {
                "result_file_format_use_ascii" : true,
                "file_format"                  : "gid"
            }
        }""")

        settings_check_process = KratosMultiphysics.Parameters("""
        {
            "reference_file_name"   : "%s",
            "output_file_name"      : "%s",
            "remove_output_file"    : true,
            "comparison_type"       : "post_res_file"
        }
        """ % (GetFilePath("eigen_postprocess_ref_files/test_postprocess_eigenvalues_process.post.res.ref"), "EigenResults/Structure_EigenResults_15_0.post.res"))

        test_model = KratosMultiphysics.Model()
        ExecuteTestPostprocessEigenvaluesProcess(settings_eigen_process, test_model)

        # check the results
        CompareTwoFilesCheckProcess(settings_check_process).Execute()

    def test_PostprocessEigenvaluesProcess_Vtk(self):
        # here the minimum settings are specified to test the default values!
        num_animation_steps = 5
        settings_eigen_process = KratosMultiphysics.Parameters("""{
            "Parameters" : {
                "result_file_format_use_ascii" : true,
                "animation_steps" : %d
            }
        }""" % num_animation_steps)

        test_model = KratosMultiphysics.Model()
        ExecuteTestPostprocessEigenvaluesProcess(settings_eigen_process, test_model)

        # check the results
        for i in range(num_animation_steps):
            settings_check_process = KratosMultiphysics.Parameters("""
            {
                "reference_file_name"   : "%s",
                "output_file_name"      : "%s",
                "remove_output_file"    : true,
                "comparison_type"       : "vtk"
            }
            """ % (GetFilePath("eigen_postprocess_ref_files/Structure_EigenResults_15_{}.vtk.ref".format(i)), "EigenResults/Structure_EigenResults_15_{}.vtk".format(i)))
            CompareTwoFilesCheckProcess(settings_check_process).Execute()


if __name__ == '__main__':
    KratosUnittest.main()
