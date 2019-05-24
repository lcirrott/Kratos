//    |  /           |
//    ' /   __| _` | __|  _ \   __|
//    . \  |   (   | |   (   |\__ `
//   _|\_\_|  \__,_|\__|\___/ ____/
//                   Multi-Physics
//
//  License:   BSD License
//      Kratos default license: kratos/license.txt
//
//  Main authors:    Vicente Mataix Ferrandiz
//

// System includes

// External includes

// Project includes
#include "testing/testing.h"
#include "geometries/tetrahedra_3d_4.h"

#include "utilities/builtin_timer.h"

/* Utilities */

namespace Kratos
{
namespace Testing
{
typedef Node<3> NodeType;
typedef std::size_t IndexSize;

KRATOS_TEST_CASE_IN_SUITE(GeometrySFAccess, KratosCoreFastSuite)
{
    auto node_1(Kratos::make_intrusive<NodeType>(1, 0.0, 0.0, 0.0));
    auto node_2(Kratos::make_intrusive<NodeType>(2, 1.0, 0.0, 0.0));
    auto node_3(Kratos::make_intrusive<NodeType>(3, 0.5, 1.0, 0.0));
    auto node_4(Kratos::make_intrusive<NodeType>(4, 0.5, 0.3, 1.0));

    const Geometry<NodeType>::Pointer p_geom(Kratos::make_shared<Tetrahedra3D4<NodeType>>(node_1, node_2, node_3, node_4));

    const std::size_t num_evaluations = 1e25;

    BuiltinTimer timer;

    for (IndexType i=0; i<num_evaluations; ++i) {
        p_geom->ShapeFunctionsValues();
    }

    std::cout << std::endl << num_evaluations << " evaluations took " << timer.ElapsedSeconds() << std::endl;
}

} // namespace Testing
}  // namespace Kratos.
