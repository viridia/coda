# Build file for Coda C++ unit test

# Unit test.
file(GLOB sample_sources *.cpp)
add_library(sample ${sample_sources})
target_link_libraries(sample coda_cpp)
set_property(TARGET sample PROPERTY CXX_STANDARD 11)
