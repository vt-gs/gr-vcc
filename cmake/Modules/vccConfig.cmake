INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_VCC vcc)

FIND_PATH(
    VCC_INCLUDE_DIRS
    NAMES vcc/api.h
    HINTS $ENV{VCC_DIR}/include
        ${PC_VCC_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    VCC_LIBRARIES
    NAMES gnuradio-vcc
    HINTS $ENV{VCC_DIR}/lib
        ${PC_VCC_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(VCC DEFAULT_MSG VCC_LIBRARIES VCC_INCLUDE_DIRS)
MARK_AS_ADVANCED(VCC_LIBRARIES VCC_INCLUDE_DIRS)

