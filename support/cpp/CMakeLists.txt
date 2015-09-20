# CMake config file for support/cpp

# Generate the config_paths.h file
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/include/coda/config.h.in
    ${CMAKE_CURRENT_BINARY_DIR}/include/coda/config.h)

file(GLOB_RECURSE headers include/*.h)
file(GLOB_RECURSE sources lib/*.cpp)

add_library(coda_cpp STATIC ${sources} ${headers})
set_property(TARGET coda_cpp PROPERTY CXX_STANDARD 11)
