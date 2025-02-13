from __future__ import print_function, absolute_import, division
import KratosMultiphysics

import KratosMultiphysics.StructuralMechanicsApplication as StructuralMechanicsApplication
import KratosMultiphysics.KratosUnittest as KratosUnittest

from math import sqrt, sin, cos, pi, exp, atan

class TestTruss3D2N(KratosUnittest.TestCase):
    def setUp(self):
        pass

    def _add_dofs(self,mp):
        KratosMultiphysics.VariableUtils().AddDof(KratosMultiphysics.DISPLACEMENT_X, KratosMultiphysics.REACTION_X,mp)
        KratosMultiphysics.VariableUtils().AddDof(KratosMultiphysics.DISPLACEMENT_Y, KratosMultiphysics.REACTION_Y,mp)
        KratosMultiphysics.VariableUtils().AddDof(KratosMultiphysics.DISPLACEMENT_Z, KratosMultiphysics.REACTION_Z,mp)

    def _add_variables(self,mp):
        mp.AddNodalSolutionStepVariable(KratosMultiphysics.DISPLACEMENT)
        mp.AddNodalSolutionStepVariable(KratosMultiphysics.REACTION)
        mp.AddNodalSolutionStepVariable(StructuralMechanicsApplication.POINT_LOAD)
        mp.AddNodalSolutionStepVariable(KratosMultiphysics.VOLUME_ACCELERATION)
        mp.AddNodalSolutionStepVariable(KratosMultiphysics.VELOCITY)
        mp.AddNodalSolutionStepVariable(KratosMultiphysics.ACCELERATION)


    def _add_constitutive_law(self,mp,elastic_flag):
        cl = StructuralMechanicsApplication.TrussPlasticityConstitutiveLaw()
        if elastic_flag:
            cl = StructuralMechanicsApplication.TrussConstitutiveLaw()
        mp.GetProperties()[0].SetValue(KratosMultiphysics.CONSTITUTIVE_LAW,cl)

    def _apply_material_properties(self,mp,dim):
        #define properties
        mp.GetProperties()[0].SetValue(KratosMultiphysics.YOUNG_MODULUS,210e9)
        mp.GetProperties()[0].SetValue(KratosMultiphysics.DENSITY,7850)
        mp.GetProperties()[0].SetValue(StructuralMechanicsApplication.CROSS_AREA,0.01)
        mp.GetProperties()[0].SetValue(StructuralMechanicsApplication.TRUSS_PRESTRESS_PK2,0)
        mp.GetProperties()[0].SetValue(StructuralMechanicsApplication.RAYLEIGH_ALPHA,0)
        mp.GetProperties()[0].SetValue(StructuralMechanicsApplication.RAYLEIGH_BETA,0)

        g = [0,0,0]
        mp.GetProperties()[0].SetValue(KratosMultiphysics.VOLUME_ACCELERATION,g)

    def _apply_material_properties_plasticity(self,mp,dim,H,A):
        mp.GetProperties()[0].SetValue(KratosMultiphysics.YOUNG_MODULUS,1000)
        mp.GetProperties()[0].SetValue(KratosMultiphysics.DENSITY,7850)
        mp.GetProperties()[0].SetValue(StructuralMechanicsApplication.CROSS_AREA,A)
        mp.GetProperties()[0].SetValue(KratosMultiphysics.YIELD_STRESS,100)
        mp.GetProperties()[0].SetValue(StructuralMechanicsApplication.HARDENING_MODULUS_1D,H)
        g = [0,0,0]
        mp.GetProperties()[0].SetValue(KratosMultiphysics.VOLUME_ACCELERATION,g)


    def _apply_BCs(self,mp,which_dof):
        if (which_dof == 'xyz'):
            KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.DISPLACEMENT_X, True, mp.Nodes)
            KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.DISPLACEMENT_Y, True, mp.Nodes)
            KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.DISPLACEMENT_Z, True, mp.Nodes)
        if (which_dof == 'xz'):
            KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.DISPLACEMENT_X, True, mp.Nodes)
            KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.DISPLACEMENT_Z, True, mp.Nodes)
        if (which_dof == 'yz'):
            KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.DISPLACEMENT_Y, True, mp.Nodes)
            KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.DISPLACEMENT_Z, True, mp.Nodes)

    def _apply_Neumann_BCs(self,mp,which_dof,load_size_dir):
        if(which_dof == 'y'):
            KratosMultiphysics.VariableUtils().SetScalarVar(StructuralMechanicsApplication.
                POINT_LOAD_Y, load_size_dir, mp.Nodes)
            # for node in mp.Nodes:
            #     node.SetSolutionStepValue(StructuralMechanicsApplication.
            #     POINT_LOAD_Y,0,load_size_dir)
        if(which_dof == 'x'):
            KratosMultiphysics.VariableUtils().SetScalarVar(StructuralMechanicsApplication.
                POINT_LOAD_X, load_size_dir, mp.Nodes)
            # for node in mp.Nodes:
            #     node.SetSolutionStepValue(StructuralMechanicsApplication.
            #     POINT_LOAD_X,0,load_size_dir)

    def _solve_linear(self,mp):
        linear_solver = KratosMultiphysics.SkylineLUFactorizationSolver()
        builder_and_solver = KratosMultiphysics.ResidualBasedBlockBuilderAndSolver(linear_solver)
        scheme = KratosMultiphysics.ResidualBasedIncrementalUpdateStaticScheme()

        compute_reactions = True
        reform_step_dofs = True
        calculate_norm_dx = False
        move_mesh_flag = True
        strategy = KratosMultiphysics.ResidualBasedLinearStrategy(mp,
                                                                scheme,
                                                                linear_solver,
                                                                builder_and_solver,
                                                                compute_reactions,
                                                                reform_step_dofs,
                                                                calculate_norm_dx,
                                                                move_mesh_flag)
        strategy.SetEchoLevel(0)

        strategy.Initialize()
        strategy.Check()
        strategy.Solve()

    def _solve_nonlinear(self,mp):
        linear_solver = KratosMultiphysics.SkylineLUFactorizationSolver()
        builder_and_solver = KratosMultiphysics.ResidualBasedBlockBuilderAndSolver(linear_solver)
        scheme = KratosMultiphysics.ResidualBasedIncrementalUpdateStaticScheme()
        convergence_criterion = KratosMultiphysics.ResidualCriteria(1e-12,1e-8)
        convergence_criterion.SetEchoLevel(0)

        max_iters = 1000
        compute_reactions = True
        reform_step_dofs = True
        move_mesh_flag = True
        strategy = KratosMultiphysics.ResidualBasedNewtonRaphsonStrategy(mp,
                                                                scheme,
                                                                linear_solver,
                                                                convergence_criterion,
                                                                builder_and_solver,
                                                                max_iters,
                                                                compute_reactions,
                                                                reform_step_dofs,
                                                                move_mesh_flag)
        strategy.SetEchoLevel(0)
        strategy.Initialize()
        strategy.Check()
        strategy.Solve()

    def _solve_dynamic(self,mp):
        #define a minimal newton raphson solver
        linear_solver = KratosMultiphysics.SkylineLUFactorizationSolver()
        builder_and_solver = KratosMultiphysics.ResidualBasedBlockBuilderAndSolver(linear_solver)
        scheme = KratosMultiphysics.ResidualBasedBossakDisplacementScheme(0.00)
        convergence_criterion = KratosMultiphysics.ResidualCriteria(1e-8,1e-8)
        convergence_criterion.SetEchoLevel(0)

        max_iters = 1000
        compute_reactions = True
        reform_step_dofs = True
        move_mesh_flag = True
        strategy = KratosMultiphysics.ResidualBasedNewtonRaphsonStrategy(mp,
                                                                scheme,
                                                                linear_solver,
                                                                convergence_criterion,
                                                                builder_and_solver,
                                                                max_iters,
                                                                compute_reactions,
                                                                reform_step_dofs,
                                                                move_mesh_flag)
        strategy.SetEchoLevel(0)

        strategy.Initialize()
        strategy.Check()
        strategy.Solve()


    def _check_results_linear(self,mp):
        #1.) check displacement result
        displacement_nodes = [mp.Nodes[1].GetSolutionStepValue(
            KratosMultiphysics.DISPLACEMENT),mp.Nodes[2].GetSolutionStepValue(
            KratosMultiphysics.DISPLACEMENT),mp.Nodes[3].GetSolutionStepValue(
            KratosMultiphysics.DISPLACEMENT)]
        for i in range(3):
            k = 0.00
            if (i == 1): k = -0.0026619856874997507
            self.assertAlmostEqual(displacement_nodes[1][i], k)
            self.assertAlmostEqual(displacement_nodes[0][i], 0)
            self.assertAlmostEqual(displacement_nodes[2][i], 0)

        #2.) check reactions
        reaction_nodes = [mp.Nodes[1].GetSolutionStepValue(
            KratosMultiphysics.REACTION),mp.Nodes[2].GetSolutionStepValue(
            KratosMultiphysics.REACTION),mp.Nodes[3].GetSolutionStepValue(
            KratosMultiphysics.REACTION)]

        Force_y = 1000000
        self.assertAlmostEqual(reaction_nodes[0][0], Force_y)
        self.assertAlmostEqual(reaction_nodes[2][0], -Force_y)
        self.assertAlmostEqual(reaction_nodes[0][1], Force_y/2)
        self.assertAlmostEqual(reaction_nodes[2][1], Force_y/2)

    def _check_results_nonlinear(self,mp,timestep,Force_i):
        ##node1
        node_temp = mp.Nodes[1]
        disp_temp = node_temp.GetSolutionStepValue(KratosMultiphysics.DISPLACEMENT)
        reac_temp = node_temp.GetSolutionStepValue(KratosMultiphysics.REACTION)
        #disp_y
        self.assertAlmostEqual(disp_temp[1], 0)
        #reaction_y
        reaction_y_node1 = Force_i*(-1)
        self.assertAlmostEqual(reac_temp[1],reaction_y_node1,6)
        #reaction_x
        reaction_x_node1 = [741464.9276515746, 1485888.977636112,
         2233316.9009164227, 2983794.615716549, 3737369.2509122863]
        self.assertAlmostEqual(reac_temp[0],reaction_x_node1[timestep], 6)

        ##node2
        node_temp = mp.Nodes[2]
        disp_temp = node_temp.GetSolutionStepValue(KratosMultiphysics.DISPLACEMENT_Y)
        reac_temp = node_temp.GetSolutionStepValue(KratosMultiphysics.REACTION)
        load_temp = node_temp.GetSolutionStepValue(StructuralMechanicsApplication.POINT_LOAD_Y)
        #pointLoad
        self.assertAlmostEqual(load_temp,Force_i)
        #reaction_x
        self.assertAlmostEqual(reac_temp[0],reaction_x_node1[timestep]*(-1), 6)
        #displacement_y
        EA = 210e9*0.01
        L = sqrt(4+1)
        L3 = L*L*L
        P_i = ((EA/(2*L3))*(disp_temp*disp_temp +2*1*disp_temp)*(disp_temp+1))
        self.assertAlmostEqual(P_i,Force_i,1)

    def _check_pre_stress_output(self,mp,force,tolerance=9):
        for element in mp.Elements:
            out = element.CalculateOnIntegrationPoints(KratosMultiphysics.FORCE,mp.ProcessInfo)
            self.assertAlmostEqual(out[0][0],force,tolerance)
            self.assertAlmostEqual(out[0][1],0.00)
            self.assertAlmostEqual(out[0][2],0.00)


    def _check_results_dynamic(self,mp,time_i):

        #analaytical free-vibration node 3
        we1 = 7917.25
        we2 = 19113.94
        y1 = 1.4142*2.874e-5
        y2 = -1.4142*4.93107e-6
        test_disp_temp = y1*(1-cos(we1*time_i))-y2*(1-cos(we2*time_i))
        simulated_disp_temp = mp.Nodes[3].GetSolutionStepValue(
            KratosMultiphysics.DISPLACEMENT_X)

        self.assertAlmostEqual(simulated_disp_temp, test_disp_temp,6)

        #analaytical free-vibration node 2
        we1 = 7917.25
        we2 = 19113.94
        y1 = 1.000*2.874e-5
        y2 = 1.000*4.93107e-6
        test_disp_temp = y1*(1-cos(we1*time_i))-y2*(1-cos(we2*time_i))
        simulated_disp_temp = mp.Nodes[2].GetSolutionStepValue(
            KratosMultiphysics.DISPLACEMENT_X)

        self.assertAlmostEqual(simulated_disp_temp, test_disp_temp,6)

    def _check_results_cable(self,mp,Force_X):

        disp_u_2 = mp.Nodes[2].GetSolutionStepValue(
        KratosMultiphysics.DISPLACEMENT_X)
        r_u_1 = mp.Nodes[1].GetSolutionStepValue(
        KratosMultiphysics.REACTION_X)
        r_u_3 = mp.Nodes[3].GetSolutionStepValue(
        KratosMultiphysics.REACTION_X)


        self.assertAlmostEqual(disp_u_2, 0.022296019142446475,6)
        self.assertAlmostEqual(r_u_1, -Force_X, 6)
        self.assertAlmostEqual(r_u_3, 0.00 ,4)

    def _check_results_dynamic_explicit(self,mp,time_i,time_step,linear_flag,scheme_name='central_differences'):

        simulated_disp_temp = mp.Nodes[2].GetSolutionStepValue(
            KratosMultiphysics.DISPLACEMENT_Y)
        test_disp_temp=[]

        if (scheme_name=='central_differences'):
            if not linear_flag:
                test_disp_temp = [-0.021876435754392846, -0.08025882554469399,
                -0.15813185652586725, -0.23777687358088162, -0.3064930326402276,
                -0.3573326497214386, -0.3873391702109082, -0.395577009293513,
                -0.3818896310557375, -0.3465605603239489, -0.2908778140223522,
                    -0.21859000122176653, -0.137959254822277, -0.06316757026754098,
                    -0.012505199445968729, -0.0013936517032937436, -0.033558757863839106,
                    -0.09855750793342796, -0.1783863153886539, -0.2562575870107372,
                    -0.32098186673316653, -0.36680529690058933, -0.3914373873640369,
                        -0.3942176190923876, -0.3750955464878065, -0.33451653033029854,
                        -0.27421215776065255, -0.19885577070221477, -0.11812448977763666,
                        -0.047582542658150095, -0.005644700007086029]
            else:
                test_disp_temp = [-0.021876435754392846, -0.08001480552613088,
                -0.15450734651949033, -0.21984629437903802, -0.2536582616084091,
                -0.24436534146715136, -0.19514961922146873, -0.12286356129128417,
                -0.05225938725829657, -0.007513405377368422, -0.0039475518645423965,
                    -0.04278284764242695, -0.11072129588924451, -0.18449938719258163,
                    -0.2388539993329007, -0.2551730052486504, -0.22786844469759693,
                    -0.16628995573849595, -0.09152326809390332, -0.029170019520337,
                    -0.0005812332236243001, -0.015546292333136365, -0.06894085558946322,
                        -0.14248153623680793, -0.21098650630318805, -0.2509982677582305,
                        -0.2488159779533806, -0.2051868973976112, -0.13505051252836275,
                        -0.06242295105627721, -0.01217337033638198]

        elif (scheme_name=='multi_stage'):
                test_disp_temp = [-0.017928408233957478, -0.07603725469469531, -0.15480249508309368,
                 -0.2364398097432736, -0.3078205614363182, -0.3615629152566572,
                  -0.3944680982865904, -0.405520197601318, -0.39453450981119104,
                   -0.3617029947296638, -0.30804598759838264, -0.23675691223215145,
                    -0.15518998752404795, -0.07641633002189718, -0.018080148760997134,
                     0.003411223679836137, -0.018737588198583684, -0.0775622817407451,
                      -0.15656059992786403, -0.23809121708132586, -0.3091522863815055,
                       -0.36247180008200336, -0.39491663588260756, -0.4054992910228645,
                        -0.3940444981430469, -0.3607540576951764, -0.30667787828648724,
                         -0.23507665118958668, -0.1534155681961326, -0.07488973412869492,
                          -0.01719384134825973]

        self.assertAlmostEqual(simulated_disp_temp, test_disp_temp[time_step],6)

    def _set_and_fill_buffer(self,mp,buffer_size,delta_time):
        # Set buffer size
        mp.SetBufferSize(buffer_size)

        # Fill buffer
        time = mp.ProcessInfo[KratosMultiphysics.TIME]
        time = time - delta_time * (buffer_size)
        mp.ProcessInfo.SetValue(KratosMultiphysics.TIME, time)
        for size in range(0, buffer_size):
            step = size - (buffer_size -1)
            mp.ProcessInfo.SetValue(KratosMultiphysics.STEP, step)
            time = time + delta_time
            #delta_time is computed from previous time in process_info
            mp.CloneTimeStep(time)

        mp.ProcessInfo[KratosMultiphysics.IS_RESTARTED] = False

    def test_truss3D2N_linear(self):
        dim = 3
        current_model = KratosMultiphysics.Model()
        mp = current_model.CreateModelPart("solid_part")
        mp.ProcessInfo.SetValue(KratosMultiphysics.DOMAIN_SIZE, dim)
        self._add_variables(mp)
        self._apply_material_properties(mp,dim)
        self._add_constitutive_law(mp,True)

        #create nodes
        mp.CreateNewNode(1,0.0,0.0,0.0)
        mp.CreateNewNode(2,2.0,1.0,0.0)
        mp.CreateNewNode(3,4.0,0.0,0.0)
        #add dofs
        self._add_dofs(mp)
        #create condition
        mp.CreateNewCondition("PointLoadCondition3D1N",1,[2],mp.GetProperties()[0])

        #create submodelparts for dirichlet boundary conditions
        bcs_xyz = mp.CreateSubModelPart("Dirichlet_XYZ")
        bcs_xyz.AddNodes([1,3])
        bcs_xz = mp.CreateSubModelPart("Dirichlet_XZ")
        bcs_xz.AddNodes([2])

        #create a submodalpart for neumann boundary conditions
        bcs_neumann = mp.CreateSubModelPart("PointLoad3D_neumann")
        bcs_neumann.AddNodes([2])
        bcs_neumann.AddConditions([1])

        #create Element
        mp.CreateNewElement("TrussLinearElement3D2N", 1, [1,2], mp.GetProperties()[0])
        mp.CreateNewElement("TrussLinearElement3D2N", 2, [2,3], mp.GetProperties()[0])

        #apply boundary conditions
        Force_Y = -1000000.00
        self._apply_BCs(bcs_xyz,'xyz')
        self._apply_BCs(bcs_xz,'xz')
        self._apply_Neumann_BCs(bcs_neumann,'y',Force_Y)

        #solve + compare
        self._solve_linear(mp)
        self._check_results_linear(mp)

    def test_truss3D2N_nonlinear(self):
        dim = 3
        current_model = KratosMultiphysics.Model()
        mp = current_model.CreateModelPart("solid_part")
        self._add_variables(mp)
        self._apply_material_properties(mp,dim)
        self._add_constitutive_law(mp,True)

        #create nodes
        mp.CreateNewNode(1,0.0,0.0,0.0)
        mp.CreateNewNode(2,2.0,1.0,0.0)
        #add dofs
        self._add_dofs(mp)
        #create condition
        mp.CreateNewCondition("PointLoadCondition3D1N",1,[2],mp.GetProperties()[0])

        #create submodelparts for dirichlet boundary conditions
        bcs_xyz = mp.CreateSubModelPart("Dirichlet_XYZ")
        bcs_xyz.AddNodes([1])
        bcs_xz = mp.CreateSubModelPart("Dirichlet_XZ")
        bcs_xz.AddNodes([2])

        #create a submodalpart for neumann boundary conditions
        bcs_neumann = mp.CreateSubModelPart("PointLoad3D_neumann")
        bcs_neumann.AddNodes([2])
        bcs_neumann.AddConditions([1])

        #create Element
        mp.CreateNewElement("TrussElement3D2N", 1, [1,2], mp.GetProperties()[0])
        #apply constant boundary conditions
        self._apply_BCs(bcs_xyz,'xyz')
        self._apply_BCs(bcs_xz,'xz')

        #incrementally increase load -> nonlinear case
        Force_y = -37000000
        time_start = 0.00
        time_end = 0.05
        time_delta = 0.01
        time_i = time_start
        time_step = 0
        while (time_i < time_end):

            time_i += time_delta
            #apply non-constant boundary conditions
            Force_i = Force_y*time_i
            self._apply_Neumann_BCs(bcs_neumann,'y',Force_i)
            #solve + compare
            self._solve_nonlinear(mp)
            self._check_results_nonlinear(mp,time_step,Force_i)
            time_step += 1

    def test_truss3D2N_prestress_nonlinear_fix(self):
        dim = 3
        current_model = KratosMultiphysics.Model()
        mp = current_model.CreateModelPart("solid_part")
        mp.ProcessInfo.SetValue(KratosMultiphysics.DOMAIN_SIZE, dim)
        self._add_variables(mp)
        self._apply_material_properties(mp,dim)
        self._add_constitutive_law(mp,True)

        mp.GetProperties()[0].SetValue(StructuralMechanicsApplication.TRUSS_PRESTRESS_PK2,1000000.00)
        #create nodes
        mp.CreateNewNode(1,0.0,0.0,0.0)
        mp.CreateNewNode(2,2.0,0.0,0.0)
        #add dofs
        self._add_dofs(mp)

        #create submodelparts for dirichlet boundary conditions
        bcs_xyz = mp.CreateSubModelPart("Dirichlet_XYZ")
        bcs_xyz.AddNodes([1])
        bcs_xz = mp.CreateSubModelPart("Dirichlet_XZ")
        bcs_xz.AddNodes([2])


        #create Element
        mp.CreateNewElement("TrussElement3D2N", 1, [1,2], mp.GetProperties()[0])

        #apply constant boundary conditions
        self._apply_BCs(bcs_xyz,'xyz')
        self._apply_BCs(bcs_xz,'xz')
        self._solve_nonlinear(mp)
        self._check_pre_stress_output(mp,10000.0)

    def test_truss3D2N_prestress_nonlinear_free(self):
        dim = 3
        current_model = KratosMultiphysics.Model()
        mp = current_model.CreateModelPart("solid_part")
        mp.ProcessInfo.SetValue(KratosMultiphysics.DOMAIN_SIZE, dim)
        self._add_variables(mp)
        self._apply_material_properties(mp,dim)
        self._add_constitutive_law(mp,True)

        mp.GetProperties()[0].SetValue(StructuralMechanicsApplication.TRUSS_PRESTRESS_PK2,1000000.00)
        #create nodes
        mp.CreateNewNode(1,0.0,0.0,0.0)
        mp.CreateNewNode(2,2.0,0.0,0.0)
        #add dofs
        self._add_dofs(mp)

        #create submodelparts for dirichlet boundary conditions
        bcs_xyz = mp.CreateSubModelPart("Dirichlet_XYZ")
        bcs_xyz.AddNodes([1])
        bcs_xz = mp.CreateSubModelPart("Dirichlet_XZ")
        bcs_xz.AddNodes([2])


        #create Element
        mp.CreateNewElement("TrussElement3D2N", 1, [1,2], mp.GetProperties()[0])

        #apply constant boundary conditions
        self._apply_BCs(bcs_xyz,'xyz')
        self._apply_BCs(bcs_xz,'yz')
        self._solve_nonlinear(mp)
        self._check_pre_stress_output(mp,0.0,6)

    def test_truss3D2N_prestress_linear_fix(self):
        dim = 3
        current_model = KratosMultiphysics.Model()
        mp = current_model.CreateModelPart("solid_part")
        mp.ProcessInfo.SetValue(KratosMultiphysics.DOMAIN_SIZE, dim)
        self._add_variables(mp)
        self._apply_material_properties(mp,dim)
        self._add_constitutive_law(mp,True)

        mp.GetProperties()[0].SetValue(StructuralMechanicsApplication.TRUSS_PRESTRESS_PK2,1000000.00)
        #create nodes
        mp.CreateNewNode(1,0.0,0.0,0.0)
        mp.CreateNewNode(2,2.0,0.0,0.0)
        #add dofs
        self._add_dofs(mp)

        #create submodelparts for dirichlet boundary conditions
        bcs_xyz = mp.CreateSubModelPart("Dirichlet_XYZ")
        bcs_xyz.AddNodes([1])
        bcs_xz = mp.CreateSubModelPart("Dirichlet_XZ")
        bcs_xz.AddNodes([2])


        #create Element
        mp.CreateNewElement("TrussLinearElement3D2N", 1, [1,2], mp.GetProperties()[0])

        #apply constant boundary conditions
        self._apply_BCs(bcs_xyz,'xyz')
        self._apply_BCs(bcs_xz,'xz')
        self._solve_linear(mp)
        self._check_pre_stress_output(mp,10000.0)

    def test_truss3D2N_prestress_linear_free(self):
        dim = 3
        current_model = KratosMultiphysics.Model()
        mp = current_model.CreateModelPart("solid_part")
        mp.ProcessInfo.SetValue(KratosMultiphysics.DOMAIN_SIZE, dim)
        self._add_variables(mp)
        self._apply_material_properties(mp,dim)
        self._add_constitutive_law(mp,True)

        mp.GetProperties()[0].SetValue(StructuralMechanicsApplication.TRUSS_PRESTRESS_PK2,1000000.00)
        #create nodes
        mp.CreateNewNode(1,0.0,0.0,0.0)
        mp.CreateNewNode(2,2.0,0.0,0.0)
        #add dofs
        self._add_dofs(mp)

        #create submodelparts for dirichlet boundary conditions
        bcs_xyz = mp.CreateSubModelPart("Dirichlet_XYZ")
        bcs_xyz.AddNodes([1])
        bcs_xz = mp.CreateSubModelPart("Dirichlet_XZ")
        bcs_xz.AddNodes([2])


        #create Element
        mp.CreateNewElement("TrussLinearElement3D2N", 1, [1,2], mp.GetProperties()[0])

        #apply constant boundary conditions
        self._apply_BCs(bcs_xyz,'xyz')
        self._apply_BCs(bcs_xz,'yz')
        self._solve_linear(mp)
        self._check_pre_stress_output(mp,0.0)

    def test_truss3D2N_dynamic(self):
        dim = 3
        current_model = KratosMultiphysics.Model()
        mp = current_model.CreateModelPart("solid_part")
        mp.ProcessInfo.SetValue(KratosMultiphysics.DOMAIN_SIZE, dim)
        self._add_variables(mp)
        self._apply_material_properties(mp,dim)
        self._add_constitutive_law(mp,True)

        #create nodes
        mp.CreateNewNode(1,0.0,0.0,0.0)
        mp.CreateNewNode(2,0.5,0.0,0.0)
        mp.CreateNewNode(3,1.0,0.0,0.0)
        #add dofs
        self._add_dofs(mp)
        #create condition
        mp.CreateNewCondition("PointLoadCondition3D1N",1,[3],mp.GetProperties()[0])
        #create submodelparts for dirichlet boundary conditions
        bcs_xyz = mp.CreateSubModelPart("Dirichlet_XYZ")
        bcs_xyz.AddNodes([1])
        bcs_yz = mp.CreateSubModelPart("Dirichlet_YZ")
        bcs_yz.AddNodes([2,3])
        #create a submodalpart for neumann boundary conditions
        bcs_neumann = mp.CreateSubModelPart("PointLoad3D_neumann")
        bcs_neumann.AddNodes([3])
        bcs_neumann.AddConditions([1])
        #create Elements
        mp.CreateNewElement("TrussElement3D2N", 1, [1,2], mp.GetProperties()[0])
        mp.CreateNewElement("TrussElement3D2N", 2, [2,3], mp.GetProperties()[0])
        #apply constant boundary conditions
        Force_X = 100000
        self._apply_BCs(bcs_xyz,'xyz')
        self._apply_BCs(bcs_yz,'yz')
        self._apply_Neumann_BCs(bcs_neumann,'x',Force_X)

        #loop over time
        time_start = 0.00
        time_end = 0.000002
        time_delta = 0.000001
        time_i = time_start
        time_step = 0
        self._set_and_fill_buffer(mp,2,time_delta)

        while (time_i <= time_end):

            time_i += time_delta
            mp.CloneTimeStep(time_i)
            #solve + compare
            self._solve_dynamic(mp)
            self._check_results_dynamic(mp,time_i)
            time_step += 1

    def test_truss3D2N_cable(self):
        dim = 3
        current_model = KratosMultiphysics.Model()
        mp = current_model.CreateModelPart("solid_part")
        mp.ProcessInfo.SetValue(KratosMultiphysics.DOMAIN_SIZE, dim)
        self._add_variables(mp)
        self._apply_material_properties(mp,dim)
        self._add_constitutive_law(mp,True)

        #create nodes
        mp.CreateNewNode(1,0.0,0.0,0.0)
        mp.CreateNewNode(2,0.5,0.0,0.0)
        mp.CreateNewNode(3,1.0,0.0,0.0)
        #add dofs
        self._add_dofs(mp)
        #create condition
        mp.CreateNewCondition("PointLoadCondition3D1N",1,[2],mp.GetProperties()[0])
        #create submodelparts for dirichlet boundary conditions
        bcs_xyz = mp.CreateSubModelPart("Dirichlet_XYZ")
        bcs_xyz.AddNodes([1,3])
        bcs_yz = mp.CreateSubModelPart("Dirichlet_YZ")
        bcs_yz.AddNodes([2])
        #create a submodalpart for neumann boundary conditions
        bcs_neumann = mp.CreateSubModelPart("PointLoad3D_neumann")
        bcs_neumann.AddNodes([2])
        bcs_neumann.AddConditions([1])
        #create Elements
        mp.CreateNewElement("CableElement3D2N", 1, [1,2], mp.GetProperties()[0])
        mp.CreateNewElement("CableElement3D2N", 2, [2,3], mp.GetProperties()[0])
        #apply constant boundary conditions
        Force_X = 100000000
        self._apply_BCs(bcs_xyz,'xyz')
        self._apply_BCs(bcs_yz,'yz')
        self._apply_Neumann_BCs(bcs_neumann,'x',Force_X)

        self._solve_nonlinear(mp)
        self._check_results_cable(mp,Force_X)

    def test_truss3D2N_dynamic_explicit_nonlinear(self):
        dim = 3
        current_model = KratosMultiphysics.Model()
        mp = current_model.CreateModelPart("solid_part")
        mp.ProcessInfo.SetValue(KratosMultiphysics.DOMAIN_SIZE, dim)
        self._add_variables(mp)
        _add_explicit_variables(mp)
        self._apply_material_properties(mp,dim)
        self._add_constitutive_law(mp,True)

        #create nodes
        mp.CreateNewNode(1,0.0,0.0,0.0)
        mp.CreateNewNode(2,2.0,1.0,0.0)
        #add dofs
        self._add_dofs(mp)
        #create condition
        mp.CreateNewCondition("PointLoadCondition3D1N",1,[2],mp.GetProperties()[0])
        #create submodelparts for dirichlet boundary conditions
        bcs_xyz = mp.CreateSubModelPart("Dirichlet_XYZ")
        bcs_xyz.AddNodes([1])
        bcs_yz = mp.CreateSubModelPart("Dirichlet_XZ")
        bcs_yz.AddNodes([2])
        #create a submodalpart for neumann boundary conditions
        bcs_neumann = mp.CreateSubModelPart("PointLoad3D_neumann")
        bcs_neumann.AddNodes([2])
        bcs_neumann.AddConditions([1])
        #create Elementsdb
        mp.CreateNewElement("TrussElement3D2N", 1, [1,2], mp.GetProperties()[0])
        #apply constant boundary conditions
        Force_Y = -24000000
        self._apply_BCs(bcs_xyz,'xyz')
        self._apply_BCs(bcs_yz,'xz')
        self._apply_Neumann_BCs(bcs_neumann,'y',Force_Y)

        #loop over time
        time_start = 0.00
        time_end = 0.012
        time_delta = 0.0004
        time_i = time_start
        time_step = 0
        self._set_and_fill_buffer(mp,2,time_delta)

        strategy_expl = _create_dynamic_explicit_strategy(mp,'central_differences')
        while (time_i <= time_end):
            time_i += time_delta
            mp.CloneTimeStep(time_i)
            #solve + compare
            strategy_expl.Solve()
            self._check_results_dynamic_explicit(mp,time_i,time_step,False)
            time_step += 1


    def test_truss3D2N_dynamic_explicit_multi_stage_nonlinear(self):
        dim = 3
        current_model = KratosMultiphysics.Model()
        mp = current_model.CreateModelPart("solid_part")
        mp.ProcessInfo.SetValue(KratosMultiphysics.DOMAIN_SIZE, dim)
        self._add_variables(mp)
        _add_explicit_variables(mp)
        self._apply_material_properties(mp,dim)
        self._add_constitutive_law(mp,True)

        #create nodes
        mp.CreateNewNode(1,0.0,0.0,0.0)
        mp.CreateNewNode(2,2.0,1.0,0.0)
        #add dofs
        self._add_dofs(mp)
        #create condition
        mp.CreateNewCondition("PointLoadCondition3D1N",1,[2],mp.GetProperties()[0])
        #create submodelparts for dirichlet boundary conditions
        bcs_xyz = mp.CreateSubModelPart("Dirichlet_XYZ")
        bcs_xyz.AddNodes([1])
        bcs_yz = mp.CreateSubModelPart("Dirichlet_XZ")
        bcs_yz.AddNodes([2])
        #create a submodalpart for neumann boundary conditions
        bcs_neumann = mp.CreateSubModelPart("PointLoad3D_neumann")
        bcs_neumann.AddNodes([2])
        bcs_neumann.AddConditions([1])
        #create Elementsdb
        mp.CreateNewElement("TrussElement3D2N", 1, [1,2], mp.GetProperties()[0])
        #apply constant boundary conditions
        Force_Y = -24000000
        self._apply_BCs(bcs_xyz,'xyz')
        self._apply_BCs(bcs_yz,'xz')
        self._apply_Neumann_BCs(bcs_neumann,'y',Force_Y)

        #loop over time
        time_start = 0.00
        time_end = 0.012
        time_delta = 0.0004
        time_i = time_start
        time_step = 0
        self._set_and_fill_buffer(mp,2,time_delta)

        strategy_expl = _create_dynamic_explicit_strategy(mp,'multi_stage')
        while (time_i <= time_end):
            time_i += time_delta
            mp.CloneTimeStep(time_i)
            #solve + compare
            strategy_expl.Solve()
            self._check_results_dynamic_explicit(mp,time_i,time_step,False,'multi_stage')
            time_step += 1

    def test_truss3D2N_dynamic_explicit_linear(self):
        dim = 3
        current_model = KratosMultiphysics.Model()
        mp = current_model.CreateModelPart("solid_part")
        mp.ProcessInfo.SetValue(KratosMultiphysics.DOMAIN_SIZE, dim)
        self._add_variables(mp)
        _add_explicit_variables(mp)
        self._apply_material_properties(mp,dim)
        self._add_constitutive_law(mp,True)

        #create nodes
        mp.CreateNewNode(1,0.0,0.0,0.0)
        mp.CreateNewNode(2,2.0,1.0,0.0)
        #add dofs
        self._add_dofs(mp)
        #create condition
        mp.CreateNewCondition("PointLoadCondition3D1N",1,[2],mp.GetProperties()[0])
        #create submodelparts for dirichlet boundary conditions
        bcs_xyz = mp.CreateSubModelPart("Dirichlet_XYZ")
        bcs_xyz.AddNodes([1])
        bcs_yz = mp.CreateSubModelPart("Dirichlet_XZ")
        bcs_yz.AddNodes([2])
        #create a submodalpart for neumann boundary conditions
        bcs_neumann = mp.CreateSubModelPart("PointLoad3D_neumann")
        bcs_neumann.AddNodes([2])
        bcs_neumann.AddConditions([1])
        #create Elementsdb
        mp.CreateNewElement("TrussLinearElement3D2N", 1, [1,2], mp.GetProperties()[0])
        #apply constant boundary conditions
        Force_Y = -24000000
        self._apply_BCs(bcs_xyz,'xyz')
        self._apply_BCs(bcs_yz,'xz')
        self._apply_Neumann_BCs(bcs_neumann,'y',Force_Y)

        #loop over time
        time_start = 0.00
        time_end = 0.012
        time_delta = 0.0004
        time_i = time_start
        time_step = 0
        self._set_and_fill_buffer(mp,2,time_delta)

        strategy_expl = _create_dynamic_explicit_strategy(mp,'central_differences')
        while (time_i <= time_end):
            time_i += time_delta
            mp.CloneTimeStep(time_i)
            #solve + compare
            strategy_expl.Solve()
            self._check_results_dynamic_explicit(mp,time_i,time_step,True)
            time_step += 1


    def test_truss3D2N_linear_plasticity(self):
        dim = 3
        current_model = KratosMultiphysics.Model()
        mp = current_model.CreateModelPart("solid_part")
        mp.ProcessInfo.SetValue(KratosMultiphysics.DOMAIN_SIZE, dim)
        self._add_variables(mp)
        self._apply_material_properties_plasticity(mp,dim,200,1.5)
        self._add_constitutive_law(mp,False)

        #create nodes
        mp.CreateNewNode(1,0.0,0.0,0.0)
        mp.CreateNewNode(2,0.0,1.2,0.0)
        #add dofs
        self._add_dofs(mp)
        #create condition
        mp.CreateNewCondition("PointLoadCondition3D1N",1,[2],mp.GetProperties()[0])

        #create submodelparts for dirichlet boundary conditions
        bcs_xyz = mp.CreateSubModelPart("Dirichlet_XYZ")
        bcs_xyz.AddNodes([1])
        bcs_xz = mp.CreateSubModelPart("Dirichlet_XZ")
        bcs_xz.AddNodes([2])

        #create a submodalpart for neumann boundary conditions
        bcs_neumann = mp.CreateSubModelPart("PointLoad3D_neumann")
        bcs_neumann.AddNodes([2])
        bcs_neumann.AddConditions([1])

        #create Element
        mp.CreateNewElement("TrussLinearElement3D2N", 1, [1,2], mp.GetProperties()[0])

        #apply boundary conditions
        Force_Y = 211.00
        self._apply_BCs(bcs_xyz,'xyz')
        self._apply_BCs(bcs_xz,'xz')
        self._apply_Neumann_BCs(bcs_neumann,'y',Force_Y)

        #solve + compare
        self._solve_nonlinear(mp)

        displacement_nodes = [mp.Nodes[1].GetSolutionStepValue(KratosMultiphysics.DISPLACEMENT),
        mp.Nodes[2].GetSolutionStepValue(KratosMultiphysics.DISPLACEMENT)]
        reaction_nodes = [mp.Nodes[1].GetSolutionStepValue(KratosMultiphysics.REACTION),
        mp.Nodes[2].GetSolutionStepValue(KratosMultiphysics.REACTION)]


        self.assertAlmostEqual(reaction_nodes[0][1], -Force_Y)
        for i in range(2): self.assertAlmostEqual(reaction_nodes[0][2*i], 0.0)
        for i in range(3): self.assertAlmostEqual(reaction_nodes[1][i], 0.0)

        plastic_disp = (0.1+((Force_Y/1.5)-100)/((1000*200)/(1000+200)))*1.2
        self.assertAlmostEqual(displacement_nodes[1][1], plastic_disp)

    def test_truss3D2N_nonlinear_plasticity(self):
        dim = 3
        current_model = KratosMultiphysics.Model()
        mp = current_model.CreateModelPart("solid_part")
        mp.ProcessInfo.SetValue(KratosMultiphysics.DOMAIN_SIZE, dim)
        self._add_variables(mp)
        self._apply_material_properties_plasticity(mp,dim,750,0.1)
        self._add_constitutive_law(mp,False)

        #create nodes
        mp.CreateNewNode(1,0.0,0.0,0.0)
        mp.CreateNewNode(2,0.0,1.2,0.0)
        #add dofs
        self._add_dofs(mp)
        #create condition
        mp.CreateNewCondition("PointLoadCondition3D1N",1,[2],mp.GetProperties()[0])

        #create submodelparts for dirichlet boundary conditions
        bcs_xyz = mp.CreateSubModelPart("Dirichlet_XYZ")
        bcs_xyz.AddNodes([1])
        bcs_xz = mp.CreateSubModelPart("Dirichlet_XZ")
        bcs_xz.AddNodes([2])

        #create a submodalpart for neumann boundary conditions
        bcs_neumann = mp.CreateSubModelPart("PointLoad3D_neumann")
        bcs_neumann.AddNodes([2])
        bcs_neumann.AddConditions([1])

        #create Element
        mp.CreateNewElement("TrussElement3D2N", 1, [1,2], mp.GetProperties()[0])

        #apply boundary conditions
        Force_Y = 14.00
        self._apply_BCs(bcs_xyz,'xyz')
        self._apply_BCs(bcs_xz,'xz')
        self._apply_Neumann_BCs(bcs_neumann,'y',Force_Y)

        #solve + compare
        self._solve_nonlinear(mp)

        displacement_nodes = [mp.Nodes[1].GetSolutionStepValue(KratosMultiphysics.DISPLACEMENT),
        mp.Nodes[2].GetSolutionStepValue(KratosMultiphysics.DISPLACEMENT)]
        reaction_nodes = [mp.Nodes[1].GetSolutionStepValue(KratosMultiphysics.REACTION),
        mp.Nodes[2].GetSolutionStepValue(KratosMultiphysics.REACTION)]


        self.assertAlmostEqual(reaction_nodes[0][1], -Force_Y,6)
        for i in range(2): self.assertAlmostEqual(reaction_nodes[0][2*i], 0.0,6)
        for i in range(3): self.assertAlmostEqual(reaction_nodes[1][i], 0.0,6)

        plastic_disp = 0.170945051
        self.assertAlmostEqual(displacement_nodes[1][1], plastic_disp)

def _add_explicit_variables(mp):
    mp.AddNodalSolutionStepVariable(StructuralMechanicsApplication.MIDDLE_VELOCITY)
    mp.AddNodalSolutionStepVariable(StructuralMechanicsApplication.FRACTIONAL_ACCELERATION)
    mp.AddNodalSolutionStepVariable(StructuralMechanicsApplication.FRACTIONAL_ANGULAR_ACCELERATION)
    mp.AddNodalSolutionStepVariable(KratosMultiphysics.NODAL_MASS)
    mp.AddNodalSolutionStepVariable(KratosMultiphysics.FORCE_RESIDUAL)
    mp.AddNodalSolutionStepVariable(KratosMultiphysics.RESIDUAL_VECTOR)
    mp.AddNodalSolutionStepVariable(StructuralMechanicsApplication.MIDDLE_ANGULAR_VELOCITY)
    mp.AddNodalSolutionStepVariable(StructuralMechanicsApplication.NODAL_INERTIA)
    mp.AddNodalSolutionStepVariable(KratosMultiphysics.MOMENT_RESIDUAL)

def _create_dynamic_explicit_strategy(mp,scheme_name):
    if (scheme_name=='central_differences'):
        scheme = StructuralMechanicsApplication.ExplicitCentralDifferencesScheme(0.00,0.00,0.00)
    elif scheme_name=='multi_stage':
        scheme = StructuralMechanicsApplication.ExplicitMultiStageKimScheme(0.33333333333333333)

    strategy = StructuralMechanicsApplication.MechanicalExplicitStrategy(mp,scheme,0,0,1)
    strategy.SetEchoLevel(0)
    return strategy



if __name__ == '__main__':
    KratosUnittest.main()

