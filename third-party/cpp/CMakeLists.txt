include(ExternalProject)

ExternalProject_Add(
  googletest
  DOWNLOAD_COMMAND ""
  PREFIX "${CMAKE_BINARY_DIR}/third-party/cpp/googletest/googletest"
  SOURCE_DIR "${CMAKE_SOURCE_DIR}/third-party/cpp/googletest/googletest"
  INSTALL_COMMAND "")
ExternalProject_Add(
  googlemock
  DOWNLOAD_COMMAND ""
  PREFIX "${CMAKE_BINARY_DIR}/third-party/cpp/googletest/googlemock"
  SOURCE_DIR "${CMAKE_SOURCE_DIR}/third-party/cpp/googletest/googlemock"
  INSTALL_COMMAND "")
