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

#if !defined(KRATOS_PMMG_UTILITIES)
#define KRATOS_PMMG_UTILITIES

// System includes

// External includes

// Project includes
#include "meshing_application.h"
#include "includes/key_hash.h"
#include "includes/model_part.h"
#include "includes/kratos_parameters.h"
#include "utilities/variable_utils.h"
#include "utilities/assign_unique_model_part_collection_tag_utility.h"
#include "processes/fast_transfer_between_model_parts_process.h"

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
///@name Kratos Globals
///@{

///@}
///@name Type Definitions
///@{

    /// Index definition
    typedef std::size_t                                               IndexType;

    /// Size definition
    typedef std::size_t                                                SizeType;

    /// Index vector
    typedef std::vector<IndexType>                              IndexVectorType;

///@}
///@name  Enum's
///@{

///@}
///@name  Functions
///@{

///@}
///@name Kratos Classes
///@{

/**
 * @class ParMmgUtilities
 * @ingroup MeshingApplication
 * @brief Provides the Kratos interface to the PARMMG library API
 * @author Luca Cirrottola
 */
template<PMMGLibrary TPMMGLibrary>
class KRATOS_API(MESHING_APPLICATION) ParMmgUtilities
{
public:

    ///@name Type Definitions
    ///@{

    /// Pointer definition of ParMmgUtilities
    KRATOS_CLASS_POINTER_DEFINITION(ParMmgUtilities);

    /// Node definition
    typedef Node <3>                                                   NodeType;
    // Geometry definition
    typedef Geometry<NodeType>                                     GeometryType;

    /// Spatial dimension
    static constexpr SizeType Dimension = 3;

    /// The type of array considered for the tensor
    typedef typename std::conditional<Dimension == 2, array_1d<double, 3>, array_1d<double, 6>>::type TensorArrayType;

    /// Double vector
    typedef std::vector<double> DoubleVectorType;

    /// Double vector map
    typedef std::unordered_map<DoubleVectorType, IndexType, KeyHasherRange<DoubleVectorType>, KeyComparorRange<DoubleVectorType> > DoubleVectorMapType;

    /// Index vector map
    typedef std::unordered_map<IndexVectorType, IndexType, KeyHasherRange<IndexVectorType>, KeyComparorRange<IndexVectorType> > IndexVectorMapType;

    /// Colors map
    typedef std::unordered_map<IndexType,IndexType> ColorsMapType;

    /// Index pair
    typedef std::pair<IndexType,IndexType> IndexPairType;

    /// Index and string vector pair
    typedef std::pair<IndexType, std::vector<std::string>> IndexStringVectorPairType;

    /// Definition of the zero tolerance
    static constexpr double ZeroTolerance = std::numeric_limits<double>::epsilon();

    ///@}
    ///@name  Enum's
    ///@{

    ///@}
    ///@name Life Cycle
    ///@{

    ///@}
    ///@name Access
    ///@{

    ///@}
    ///@name Inquiry
    ///@{

    ///@}
    ///@name Input and output
    ///@{

    ///@}
    ///@name Friends
    ///@{

    ///@}
    ///@name Operators
    ///@{

    ///@}
    ///@name Operations
    ///@{

    /**
     * @brief This method sets the echo level
     * @param[in] EchoLevel Sets the echo level
     */
    void SetEchoLevel(const SizeType EchoLevel);

    /**
     * @brief This method gets the echo level
     * @return mEchoLevel Gets the echo level
     */
    SizeType GetEchoLevel();

    /**
     * @brief Here the verbosity is set
     */
    void InitVerbosity();

    /**
     * @brief Here the verbosity is set using the API
     * @param[in] VerbosityPMMG The equivalent verbosity level in the PMMG API
     */
    void InitVerbosityParameter(const IndexType VerbosityPMMG);

    ///@}
    ///@name Access
    ///@{


    ///@}
    ///@name Inquiry
    ///@{


    ///@}
    ///@name Input and output
    ///@{

    /// Turn back information as a string.
    std::string Info() const // override
    {
        return "ParMmgUtilities";
    }

    /// Print information about this object.
    void PrintInfo(std::ostream& rOStream) const // override
    {
        rOStream << "ParMmgUtilities";
    }

    /// Print object's data.
    void PrintData(std::ostream& rOStream) const // override
    {
    }

protected:

    ///@name Protected Member Variables
    ///@{

    ///@}
    ///@name Protected member Variables
    ///@{

    ///@}
    ///@name Protected Operators
    ///@{

    ///@}
    ///@name Protected Operations
    ///@{

    ///@}
    ///@name Protected  Access
    ///@{

    ///@}
    ///@name Protected Inquiry
    ///@{

    ///@}
    ///@name Protected LifeCycle
    ///@{

    ///@}

private:
    ///@name Static Member Variables
    ///@{

    ///@}
    ///@name Member Variables
    ///@{

    SizeType mEchoLevel = 0;                                               /// The echo level of the utilities
    bool mRemoveRegions = false;                                           /// Cuttig-out specified regions during surface remeshing
    DiscretizationOption mDiscretization = DiscretizationOption::STANDARD; /// Discretization The discretization type

    ///@}
    ///@name Private Operators
    ///@{

    ///@}
    ///@name Private Operations
    ///@{

    /**
     * @brief Sets a flag according to a given status over all submodelparts
     * @param rFlag flag to be set
     * @param FlagValue flag value to be set
     */
    void ResursivelyAssignFlagEntities(
        ModelPart& rModelPart,
        const Flags& rFlag,
        const bool FlagValue
        )
    {
        // We call it recursively
        for (auto& r_sub_model_part : rModelPart.SubModelParts()) {
            VariableUtils().SetFlag(rFlag, FlagValue, r_sub_model_part.Conditions());
            VariableUtils().SetFlag(rFlag, FlagValue, r_sub_model_part.Elements());
            ResursivelyAssignFlagEntities(r_sub_model_part, rFlag, FlagValue);
        }
    }

    ///@}
    ///@name Private  Access
    ///@{


    ///@}
    ///@name Private Inquiry
    ///@{


    ///@}
    ///@name Un accessible methods
    ///@{

//     /// Assignment operator.
//     MmgUtilities& operator=(MmgUtilities const& rOther);

//     /// Copy constructor.
//     MmgUtilities(MmgUtilities const& rOther);

    ///@}

};// class MmgUtilities
///@}

///@name Type Definitions
///@{


///@}
///@name Input and output
///@{

/// input stream function
template<PMMGLibrary TPMMGLibrary>
inline std::istream& operator >> (std::istream& rIStream,
                                  ParMmgUtilities<TPMMGLibrary>& rThis);

/// output stream function
template<PMMGLibrary TPMMGLibrary>
inline std::ostream& operator << (std::ostream& rOStream,
                                  const ParMmgUtilities<TPMMGLibrary>& rThis)
{
    rThis.PrintInfo(rOStream);
    rOStream << std::endl;
    rThis.PrintData(rOStream);

    return rOStream;
}

}// namespace Kratos.
#endif /* KRATOS_PMMG_UTILITIES defined */
