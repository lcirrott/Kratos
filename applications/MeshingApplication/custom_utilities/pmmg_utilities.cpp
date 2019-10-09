// KRATOS  __  __ _____ ____  _   _ ___ _   _  ____
//        |  \/  | ____/ ___|| | | |_ _| \ | |/ ___|
//        | |\/| |  _| \___ \| |_| || ||  \| | |  _
//        | |  | | |___ ___) |  _  || || |\  | |_| |
//        |_|  |_|_____|____/|_| |_|___|_| \_|\____| APPLICATION
//
//  License:		 BSD License
//                       license: MeshingApplication/license.txt
//
//  Main authors:    Luca Cirrottola, Vicente Mataix Ferrandiz
//

// System includes
#include <unordered_set>

// External includes
/* The includes related with the MMG library */
#if !defined(PMMG_INCLUDES)
#define PMMG_INCLUDES
#include "parmmg/libparmmg.h"
#include "mmg/mmg3d/libmmg3d.h"
#endif /* PMMG_INCLUDES defined */

// Project includes
#include "containers/model.h"
#include "utilities/compare_elements_and_conditions_utility.h"
#include "custom_utilities/mmg_utilities.h"

// NOTE: The following contains the license of the MMG library
/* =============================================================================
**  Copyright (c) Bx INP/Inria/UBordeaux/UPMC, 2004- .
**
**  mmg is free software: you can redistribute it and/or modify it
**  under the terms of the GNU Lesser General Public License as published
**  by the Free Software Foundation, either version 3 of the License, or
**  (at your option) any later version.
**
**  mmg is distributed in the hope that it will be useful, but WITHOUT
**  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
**  FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
**  License for more details.
**
**  You should have received a copy of the GNU Lesser General Public
**  License and of the GNU General Public License along with mmg (in
**  files COPYING.LESSER and COPYING). If not, see
**  <http://www.gnu.org/licenses/>. Please read their terms carefully and
**  use this copy of the mmg distribution only if you accept them.
** =============================================================================
*/

namespace Kratos
{


template<PMMGLibrary TPMMGLibrary>
void ParMmgUtilities<TPMMGLibrary>::SetEchoLevel(const SizeType EchoLevel)
{
    mEchoLevel = EchoLevel;
}

/***********************************************************************************/
/***********************************************************************************/

template<PMMGLibrary TPMMGLibrary>
SizeType ParMmgUtilities<TPMMGLibrary>::GetEchoLevel()
{
    return mEchoLevel;
}

/***********************************************************************************/
/***********************************************************************************/

template<PMMGLibrary TPMMGLibrary>
void ParMmgUtilities<TPMMGLibrary>::InitVerbosity()
{
    /* We set the PMMG verbosity */
    int verbosity_pmmg;
    if (mEchoLevel == 0)
        verbosity_pmmg = -1;
    else if (mEchoLevel == 1)
        verbosity_pmmg = 0; // NOTE: This way just the essential info from MMG will be printed, but the custom message will appear
    else if (mEchoLevel == 2)
        verbosity_pmmg = 3;
    else if (mEchoLevel == 3)
        verbosity_pmmg = 5;
    else
        verbosity_pmmg = 10;

//    InitVerbosityParameter(verbosity_pmmg);
}

/***********************************************************************************/
/***********************************************************************************/

//template<>
//void MmgUtilities<MMGLibrary::MMG3D>::InitVerbosityParameter(const IndexType VerbosityMMG)
//{
//    KRATOS_ERROR_IF( !MMG3D_Set_iparameter(mMmgMesh,mMmgSol,MMG3D_IPARAM_verbose, VerbosityMMG) ) << "Unable to set verbosity" << std::endl;
//}

/***********************************************************************************/
/***********************************************************************************/

//template class MmgUtilities<MMGLibrary::MMG2D>;
//template class MmgUtilities<MMGLibrary::MMG3D>;
//template class MmgUtilities<MMGLibrary::MMGS>;

}// namespace Kratos.
