# Build file for Coda C++ unit test

# Unit test.
file(GLOB unit_sources *.cpp)
add_executable(unittest ${unit_sources})
target_link_libraries(unittest coda_cpp gtest pthread)

# ${CMAKE_THREAD_LIBS_INIT}
