# Build file for Coda C++ unit test

# Locate Google Test
ExternalProject_Get_Property(googletest BINARY_DIR)

# Unit test.
file(GLOB unit_sources *.cpp)
add_executable(unittest ${unit_sources})
add_dependencies(unittest googletest)
target_link_libraries(unittest
  coda_cpp
  ${BINARY_DIR}/${CMAKE_FIND_LIBRARY_PREFIXES}gtest${CMAKE_STATIC_LIBRARY_SUFFIX}
  pthread)

# ${CMAKE_THREAD_LIBS_INIT}
