# Build file for Coda C++ unit test

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../data)

# Unit test.
file(GLOB unit_sources *.cpp)
add_executable(unittest ${unit_sources})
target_link_libraries(unittest coda_cpp sample gtest gmock pthread)
set_property(TARGET unittest PROPERTY CXX_STANDARD 11)

# ${CMAKE_THREAD_LIBS_INIT}
