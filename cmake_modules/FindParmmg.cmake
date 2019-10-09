## =============================================================================
##  This file is part of the mmg software package for the tetrahedral
##  mesh modification.
##  Copyright (c) Inria - IMB (Université de Bordeaux) - LJLL (UPMC), 2004- .
##
##  mmg is free software: you can redistribute it and/or modify it
##  under the terms of the GNU Lesser General Public License as published
##  by the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.
##
##  mmg is distributed in the hope that it will be useful, but WITHOUT
##  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
##  FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
##  License for more details.
##
##  You should have received a copy of the GNU Lesser General Public
##  License and of the GNU General Public License along with mmg (in
##  files COPYING.LESSER and COPYING). If not, see
##  <http://www.gnu.org/licenses/>. Please read their terms carefully and
##  use this copy of the mmg distribution only if you accept them.
## =============================================================================
#
# This package define the PMMG_INCLUDE_DIR and the PMMG_LIBRARY variables.  To
# link with the ParMmg library using CMake add the following lines to your
# CMakeLists.txt:
#
# INCLUDE(FindParmmg.cmake)
#
# INCLUDE_DIRECTORIES(${PMMG_INCLUDE_DIR})
#
# TARGET_LINK_LIBRARIES( ${YOUR_TARGET} ${PMMG_LIBRARY})


IF ((NOT WIN32) AND (NOT WIN64))
  SET ( PMMG_INCLUDE_DIR PMMG_INCLUDE_DIR-NOTFOUND )
  SET ( PMMG_LIBRARY PMMG_LIBRARY-NOTFOUND )
ENDIF()

FIND_PATH(PMMG_INCLUDE_DIR
  NAMES parmmg/libparmmg.h
  HINTS ${PMMG_INCLUDE_DIR}
  $ENV{PMMG_INCLUDE_DIR}
  $ENV{HOME}/include/
  ${PMMG_DIR}/include/
  $ENV{PMMG_DIR}/include/
  PATH_SUFFIXES
  DOC "Directory of parmmg Headers")

# Check for parmmg library
FIND_LIBRARY(PMMG_LIBRARY
  NAMES parmmg parmmg${PMMG_LIB_SUFFIX}
  HINTS ${PMMG_LIBRARY}
  $ENV{PMMG_LIBRARY}
  $ENV{HOME}/lib
  ${PMMG_DIR}/lib
  $ENV{PMMG_DIR}/lib
  DOC "The parmmg library"
  )

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(PMMG DEFAULT_MSG
  PMMG_INCLUDE_DIR PMMG_LIBRARY)

IF ( NOT PMMG_FOUND )
   MESSAGE (WARNING "\nPARMMG not found: you can set the 'PMMG_DIR' environment"
   " variable or the 'PMMG_DIR' CMake variable to your PARMMG directory path"
   " to help us to fill the PARMMG library paths.\n" )
ENDIF () 
