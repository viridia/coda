include(ExternalProject)

ExternalProject_Add(
  project_googletest
  DOWNLOAD_COMMAND ""
  PREFIX "${CMAKE_BINARY_DIR}/third-party/cpp/googletest/googletest"
  SOURCE_DIR "${CMAKE_SOURCE_DIR}/third-party/cpp/googletest/googletest"
  INSTALL_COMMAND "")
ExternalProject_Add(
  project_googlemock
  DOWNLOAD_COMMAND ""
  PREFIX "${CMAKE_BINARY_DIR}/third-party/cpp/googletest/googlemock"
  SOURCE_DIR "${CMAKE_SOURCE_DIR}/third-party/cpp/googletest/googlemock"
  INSTALL_COMMAND "")

# Locate Google Test
ExternalProject_Get_Property(project_googletest BINARY_DIR)

# Gtest library
add_library(gtest STATIC IMPORTED GLOBAL)
set_property(TARGET gtest PROPERTY IMPORTED_LOCATION
   ${BINARY_DIR}/${CMAKE_FIND_LIBRARY_PREFIXES}gtest${CMAKE_STATIC_LIBRARY_SUFFIX})
add_dependencies(gtest project_googletest)

# Locate Google Mock
ExternalProject_Get_Property(project_googlemock BINARY_DIR)

# Gmock library
add_library(gmock STATIC IMPORTED GLOBAL)
set_property(TARGET gmock PROPERTY IMPORTED_LOCATION
   ${BINARY_DIR}/${CMAKE_FIND_LIBRARY_PREFIXES}gmock${CMAKE_STATIC_LIBRARY_SUFFIX})
add_dependencies(gmock project_googlemock)
